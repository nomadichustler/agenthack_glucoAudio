import numpy as np
import torch
from transformers import Wav2Vec2Model, Wav2Vec2Processor
import librosa

class EmbeddingAgent:
    """Agent for extracting embeddings from audio data"""
    
    def __init__(self):
        # Load model and processor
        self.model = None
        self.processor = None
    
    def _load_model(self):
        """Lazy loading of the model to save resources"""
        if self.model is None:
            try:
                self.model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
                self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to simple feature extraction if model loading fails
                self.model = None
                self.processor = None
    
    async def extract_embeddings(self, processed_audio):
        """Extract wav2vec2.0 embeddings from audio"""
        waveform = processed_audio['waveform']
        sample_rate = processed_audio['sample_rate']
        
        # Try to use transformer model if available
        try:
            self._load_model()
            if self.model and self.processor:
                return await self._extract_with_wav2vec(waveform, sample_rate)
        except Exception as e:
            print(f"Error extracting embeddings with wav2vec: {e}")
        
        # Fallback to traditional feature extraction
        return await self._extract_fallback_features(waveform, sample_rate)
    
    async def _extract_with_wav2vec(self, waveform, sample_rate):
        """Extract embeddings using wav2vec2 model"""
        # Resample if needed
        if sample_rate != 16000:
            waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000
        
        # Convert to tensor
        input_values = self.processor(
            waveform, 
            sampling_rate=sample_rate, 
            return_tensors="pt"
        ).input_values
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(input_values)
            embeddings = outputs.last_hidden_state.mean(dim=1).numpy()[0]
        
        # Ensure we have a 512-dimensional vector
        if len(embeddings) > 512:
            embeddings = embeddings[:512]
        elif len(embeddings) < 512:
            # Pad with zeros if needed
            embeddings = np.pad(embeddings, (0, 512 - len(embeddings)))
        
        return embeddings.tolist()
    
    async def _extract_fallback_features(self, waveform, sample_rate):
        """Extract fallback features when wav2vec is not available"""
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=40)
        mfcc_features = np.mean(mfccs, axis=1)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=waveform, sr=sample_rate)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=waveform, sr=sample_rate)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=waveform, sr=sample_rate)
        spectral_contrast = librosa.feature.spectral_contrast(y=waveform, sr=sample_rate)
        
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=waveform, sr=sample_rate)
        
        # Combine features
        features = np.concatenate([
            mfcc_features,
            np.mean(spectral_centroid, axis=1),
            np.mean(spectral_bandwidth, axis=1),
            np.mean(spectral_rolloff, axis=1),
            np.mean(spectral_contrast, axis=1),
            np.mean(chroma, axis=1)
        ])
        
        # Pad or truncate to 512 dimensions
        if len(features) > 512:
            features = features[:512]
        elif len(features) < 512:
            features = np.pad(features, (0, 512 - len(features)))
        
        return features.tolist()