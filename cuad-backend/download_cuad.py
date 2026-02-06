import json
import requests
import os

# Alternative CUAD dataset sources
CUAD_SOURCES = [
    # Hugging Face direct download
    "https://huggingface.co/datasets/contracts/CUAD/resolve/main/CUAD_v1.json",
    # Backup from CUAD repo (different path)
    "https://raw.githubusercontent.com/TheAtticusProject/cuad/master/data/CUAD_v1.json",
]

def download_cuad():
    """Download and save the CUAD dataset"""
    print("Attempting to download CUAD dataset...")
    
    # Try multiple sources
    for source_url in CUAD_SOURCES:
        try:
            print(f"Trying: {source_url}")
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            
            # Parse the JSON
            data = response.json()
            
            # Save locally
            with open('data/CUAD_v1.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Success! Dataset saved from {source_url}")
            print(f"  Contains {len(data['data'])} legal documents")
            
            # Print some stats
            clauses = []
            for doc in data['data']:
                for para in doc['paragraphs']:
                    for qa in para['qas']:
                        clauses.append({
                            'question': qa['question'],
                            'clause_text': para['context'],
                            'clause_type': qa['id'].split('_')[0],
                            'is_impossible': qa.get('is_impossible', False)
                        })
            
            print(f"\nExtracted {len(clauses)} unique legal clauses")
            print("\nSample clause types:")
            from collections import Counter
            types = Counter([c['clause_type'] for c in clauses])
            for t, count in types.most_common(10):
                print(f"  {t}: {count}")
            
            # Also save a sample for testing
            with open('data/CUAD_sample.json', 'w') as f:
                json.dump(clauses[:50], f, indent=2)
            print(f"\n✓ Sample saved to data/CUAD_sample.json")
            
            return clauses
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue
    
    # If all sources fail, use a minimal sample dataset
    print("\n⚠️  All download sources failed. Creating minimal sample dataset...")
    create_minimal_sample()
    return []

def create_minimal_sample():
    """Create a minimal CUAD sample for testing"""
    sample_data = {
        "version": "1.0",
        "data": [
            {
                "title": "Sample_Confidentiality_Agreement",
                "paragraphs": [
                    {
                        "id": "confidentiality_1",
                        "context": "The Receiving Party shall hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the Disclosing Party. The Receiving Party shall carefully restrict access to Confidential Information to employees, contractors, and third parties as is reasonably required and shall require those persons to sign nondisclosure restrictions at least as protective as those in this Agreement.",
                        "qas": [
                            {
                                "id": "confidentiality_1",
                                "question": "What are the obligations of the receiving party regarding confidential information?",
                                "answers": [],
                                "is_impossible": False
                            }
                        ]
                    },
                    {
                        "id": "termination_1",
                        "context": "This Agreement may be terminated by either party upon thirty (30) days written notice to the other party. Upon termination, all rights and obligations of the parties shall cease, except that obligations of confidentiality and any provisions that by their nature should survive termination shall survive.",
                        "qas": [
                            {
                                "id": "termination_1",
                                "question": "What is the notice period for termination?",
                                "answers": [],
                                "is_impossible": False
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    with open('data/CUAD_v1.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("✓ Created minimal sample dataset with 2 legal clauses")
    print("  You can download the full dataset manually from:")
    print("  https://huggingface.co/datasets/contracts/CUAD")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    clauses = download_cuad()
    
    if clauses:
        print("\n✅ CUAD dataset ready!")
        print(f"Total clauses: {len(clauses)}")
        print("\nNext steps:")
        print("1. Run: python3 -c 'from cuad_loader import CUADLoader; loader = CUADLoader(); loader.load_and_process_cuad()'")
        print("2. Start server: uvicorn main:app --reload")
    else:
        print("\n⚠️  Using minimal sample dataset.")
        print("For full functionality, download CUAD manually:")
        print("1. Visit: https://huggingface.co/datasets/contracts/CUAD")
        print("2. Download CUAD_v1.json")
        print("3. Place it in: data/CUAD_v1.json")