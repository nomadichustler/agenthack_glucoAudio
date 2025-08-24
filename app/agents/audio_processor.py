import numpy as np
import librosa
import os
import tempfile

class AudioProcessorAgent:
    """Agent for audio preprocessing and quality assessment"""
    
    async def process_audio(self, audio_data):
        """Process audio data"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            audio_data.save(temp_path)
            
            try:               
                processed_audio = await self.preprocess_audio(temp_path)               
                quality_metrics = await self.assess_quality(processed_audio)
                
                return {
                    "processed_audio": processed_audio,
                    "quality_metrics": quality_metrics
                }
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    async def preprocess_audio(self, audio_path):
        """Preprocess audio file with noise reduction and normalization"""
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Trim silence
        y, _ = librosa.effects.trim(y, top_db=20)
        
        # Normalize audio
        y = librosa.util.normalize(y)
        
        # Apply pre-emphasis filter
        y_filtered = librosa.effects.preemphasis(y)
        
        return {
            'waveform': y_filtered,
            'sample_rate': sr,
            'duration': len(y_filtered) / sr
        }
    
    async def assess_quality(self, processed_audio):
        """Assess audio quality metrics"""
        waveform = processed_audio['waveform']
        sr = processed_audio['sample_rate']
        
        # Calculate signal-to-noise ratio
        signal_power = np.mean(waveform ** 2)
        noise_estimate = np.var(waveform) * 0.1  
        snr = 10 * np.log10(signal_power / noise_estimate) if noise_estimate > 0 else 30.0
        
        # Calculate clarity score based on spectral centroid
        cent = librosa.feature.spectral_centroid(y=waveform, sr=sr)[0]
        clarity_score = min(100, max(0, int(np.mean(cent) / 50)))
        
        # Calculate spectral quality
        spec_bw = librosa.feature.spectral_bandwidth(y=waveform, sr=sr)[0]
        spectral_quality = min(100, max(0, int(100 - np.mean(spec_bw) / 100)))
        
        return {
            'snr': float(snr),
            'duration': processed_audio['duration'],
            'clarity': clarity_score,
            'spectral_quality': spectral_quality
        }
    
    async def extract_features(self, processed_audio):
        """Extract audio features for embedding"""
        waveform = processed_audio['waveform']
        sr = processed_audio['sample_rate']
        
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=13)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=waveform, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=waveform, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=waveform, sr=sr)
        
        # Extract zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(waveform)
        
        # Combine features
        features = {
            'mfccs': mfccs.mean(axis=1).tolist(),
            'spectral_centroid': float(np.mean(spectral_centroid)),
            'spectral_bandwidth': float(np.mean(spectral_bandwidth)),
            'spectral_rolloff': float(np.mean(spectral_rolloff)),
            'zero_crossing_rate': float(np.mean(zcr))
        }
        
        return features