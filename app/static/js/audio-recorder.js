/**
 * Audio Recorder for glucoAudio
 * Handles voice recording with waveform visualization
 */

class AudioRecorder {
    constructor(options = {}) {
        // Configuration
        this.options = {
            canvas: null,
            onRecordingStart: null,
            onRecordingStop: null,
            onRecordingProgress: null,
            onError: null,
            maxDuration: 15, // seconds
            ...options
        };
        
        // State
        this.mediaRecorder = null;
        this.audioContext = null;
        this.analyser = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.startTime = null;
        this.recordingInterval = null;
        this.audioBlob = null;
        this.audioUrl = null;
        
        // Canvas context for visualization
        this.canvasCtx = this.options.canvas ? this.options.canvas.getContext('2d') : null;
        
        // Bind methods
        this.startRecording = this.startRecording.bind(this);
        this.stopRecording = this.stopRecording.bind(this);
        this.visualize = this.visualize.bind(this);
        this.handleRecordingProgress = this.handleRecordingProgress.bind(this);
    }
    
    /**
     * Start recording audio
     */
    async startRecording() {
        try {
            // Reset state
            this.audioChunks = [];
            this.audioBlob = null;
            this.audioUrl = null;
            
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Set up audio context for visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(stream);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            source.connect(this.analyser);
            
            // Create media recorder
            this.mediaRecorder = new MediaRecorder(stream);
            
            // Event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                // Create audio blob
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.audioUrl = URL.createObjectURL(this.audioBlob);
                
                // Stop visualization
                cancelAnimationFrame(this.animationFrame);
                
                // Stop interval timer
                clearInterval(this.recordingInterval);
                
                // Callback
                if (this.options.onRecordingStop) {
                    this.options.onRecordingStop({
                        blob: this.audioBlob,
                        url: this.audioUrl,
                        duration: (Date.now() - this.startTime) / 1000
                    });
                }
                
                // Clean up
                stream.getTracks().forEach(track => track.stop());
                this.isRecording = false;
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            this.startTime = Date.now();
            
            // Start visualization
            if (this.canvasCtx) {
                this.visualize();
            }
            
            // Start progress timer
            this.recordingInterval = setInterval(this.handleRecordingProgress, 100);
            
            // Callback
            if (this.options.onRecordingStart) {
                this.options.onRecordingStart();
            }
            
            // Auto-stop after max duration
            setTimeout(() => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            }, this.options.maxDuration * 1000);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
        }
    }
    
    /**
     * Stop recording audio
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
        }
    }
    
    /**
     * Handle recording progress
     */
    handleRecordingProgress() {
        if (!this.isRecording) return;
        
        const elapsed = (Date.now() - this.startTime) / 1000;
        const remaining = this.options.maxDuration - elapsed;
        
        if (this.options.onRecordingProgress) {
            this.options.onRecordingProgress({
                elapsed,
                remaining,
                percent: (elapsed / this.options.maxDuration) * 100
            });
        }
        
        // Auto-stop if we reach max duration
        if (remaining <= 0) {
            this.stopRecording();
        }
    }
    
    /**
     * Visualize audio waveform on canvas
     */
    visualize() {
        if (!this.canvasCtx || !this.analyser) return;
        
        const canvas = this.canvasCtx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        this.canvasCtx.clearRect(0, 0, width, height);
        
        const draw = () => {
            if (!this.isRecording) return;
            
            this.animationFrame = requestAnimationFrame(draw);
            
            this.analyser.getByteTimeDomainData(dataArray);
            
            this.canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            this.canvasCtx.fillRect(0, 0, width, height);
            
            this.canvasCtx.lineWidth = 2;
            this.canvasCtx.strokeStyle = '#FFFFFF';
            this.canvasCtx.beginPath();
            
            const sliceWidth = width / bufferLength;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * height / 2;
                
                if (i === 0) {
                    this.canvasCtx.moveTo(x, y);
                } else {
                    this.canvasCtx.lineTo(x, y);
                }
                
                x += sliceWidth;
            }
            
            this.canvasCtx.lineTo(canvas.width, canvas.height / 2);
            this.canvasCtx.stroke();
        };
        
        draw();
    }
    
    /**
     * Get the recorded audio blob
     */
    getAudioBlob() {
        return this.audioBlob;
    }
    
    /**
     * Get the recorded audio URL
     */
    getAudioUrl() {
        return this.audioUrl;
    }
    
    /**
     * Check if browser supports recording
     */
    static isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }
}
