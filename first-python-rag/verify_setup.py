"""
Verification script to check if the local Jina V3 model is available and loadable.
"""
import os
import sys
from pathlib import Path

def verify_model_path():
    """Check if the model path exists."""
    model_path = Path(r"C:\models\huggingface\JinaV3\jina-embeddings-v3")
    
    print("=" * 60)
    print("Verifying Local Model Setup")
    print("=" * 60)
    
    if not model_path.exists():
        print(f"❌ ERROR: Model path does not exist!")
        print(f"   Expected path: {model_path}")
        print(f"\n   Please ensure the Jina V3 model is downloaded to this location.")
        return False
    
    print(f"✓ Model path exists: {model_path}")
    return True

def verify_model_loading():
    """Try to load the model using HuggingFace AutoModel."""
    try:
        print("\nAttempting to load the model...")
        from transformers import AutoModel, AutoTokenizer
        
        model_path = r"C:\models\huggingface\JinaV3\jina-embeddings-v3"
        
        # Try loading the tokenizer
        print("  - Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("    ✓ Tokenizer loaded successfully")
        
        # Try loading the model
        print("  - Loading model...")
        model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        print("    ✓ Model loaded successfully")
        
        print(f"\n✓ Model verification complete!")
        print(f"  Model type: {type(model).__name__}")
        print(f"  Config: {model.config.model_type if hasattr(model.config, 'model_type') else 'N/A'}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ERROR: Missing required packages!")
        print(f"   {str(e)}")
        print(f"\n   Please install requirements: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to load model!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Possible causes:")
        print(f"   - Model files are corrupted or incomplete")
        print(f"   - Incompatible transformers version")
        print(f"   - Missing model configuration files")
        return False

def main():
    """Main verification routine."""
    # Check path
    if not verify_model_path():
        sys.exit(1)
    
    # Check model loading
    if not verify_model_loading():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All verification checks passed!")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
