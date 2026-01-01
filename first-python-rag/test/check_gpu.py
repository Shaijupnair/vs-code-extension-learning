"""
Quick script to check GPU availability and usage.
"""

import torch

print("=" * 80)
print("GPU Detection Check")
print("=" * 80)

# Check CUDA availability
print(f"\n1️⃣ CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"2️⃣ CUDA Version: {torch.version.cuda}")
    print(f"3️⃣ GPU Count: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        print(f"\n📊 GPU {i}:")
        print(f"   Name: {torch.cuda.get_device_name(i)}")
        print(f"   Memory Total: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
        
    # Check current device
    if torch.cuda.current_device() is not None:
        current = torch.cuda.current_device()
        print(f"\n✓ Current Device: GPU {current} ({torch.cuda.get_device_name(current)})")
    
    # Test tensor on GPU
    print("\n4️⃣ Testing GPU tensor creation...")
    try:
        test_tensor = torch.randn(1000, 1000).cuda()
        print(f"   ✓ Successfully created tensor on GPU")
        print(f"   Device: {test_tensor.device}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
else:
    print("\n⚠️ CUDA not available - will use CPU only")
    print("\nPossible reasons:")
    print("  1. PyTorch not installed with CUDA support")
    print("  2. GPU drivers not properly installed")
    print("  3. CUDA toolkit not installed")
    
print("\n" + "=" * 80)
