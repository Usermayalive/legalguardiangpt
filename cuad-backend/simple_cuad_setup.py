import json
import os
import requests

def setup_cuad_minimal():
    """Create a minimal working CUAD dataset for development"""
    
    # Create sample legal clauses (realistic examples)
    sample_clauses = [
        {
            "text": "Confidential Information shall mean all information disclosed by one party to the other, whether before or after the Effective Date, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure.",
            "type": "Confidentiality",
            "risk": "Medium"
        },
        {
            "text": "The Receiving Party agrees to use the Confidential Information only for the Purpose and not to disclose such information to any third party without the prior written consent of the Disclosing Party.",
            "type": "Confidentiality",
            "risk": "High"
        },
        {
            "text": "This Agreement shall terminate automatically upon the completion of the Services, or may be terminated by either party upon thirty (30) days written notice.",
            "type": "Termination",
            "risk": "Low"
        },
        {
            "text": "Upon termination, each party shall return or destroy all Confidential Information of the other party in its possession or control.",
            "type": "Termination",
            "risk": "Medium"
        },
        {
            "text": "Neither party shall be liable for any indirect, incidental, special, consequential, or punitive damages, including lost profits or revenue.",
            "type": "Liability",
            "risk": "High"
        },
        {
            "text": "Each party shall indemnify and hold harmless the other party from and against any claims, damages, or losses arising from its breach of this Agreement.",
            "type": "Indemnification",
            "risk": "High"
        },
        {
            "text": "All disputes arising under this Agreement shall be resolved by binding arbitration in accordance with the rules of the American Arbitration Association.",
            "type": "Dispute_Resolution",
            "risk": "Medium"
        },
        {
            "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of New York, without regard to its conflict of laws principles.",
            "type": "Governing_Law",
            "risk": "Low"
        },
        {
            "text": "All notices required under this Agreement shall be in writing and shall be deemed given when delivered personally or by certified mail.",
            "type": "Notices",
            "risk": "Low"
        },
        {
            "text": "No amendment or modification of this Agreement shall be valid unless in writing and signed by both parties.",
            "type": "Amendment",
            "risk": "Medium"
        }
    ]
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save as JSON
    with open('data/sample_clauses.json', 'w') as f:
        json.dump(sample_clauses, f, indent=2)
    
    # Also create a minimal CUAD format file
    cuad_format = {
        "version": "1.0",
        "data": []
    }
    
    for i, clause in enumerate(sample_clauses):
        cuad_format["data"].append({
            "title": f"Sample_Document_{i}",
            "paragraphs": [{
                "id": f"{clause['type'].lower()}_{i}",
                "context": clause["text"],
                "qas": [{
                    "id": f"{clause['type'].lower()}_{i}",
                    "question": f"What does this {clause['type']} clause specify?",
                    "answers": [],
                    "is_impossible": False
                }]
            }]
        })
    
    with open('data/CUAD_v1.json', 'w') as f:
        json.dump(cuad_format, f, indent=2)
    
    print("✅ Created sample legal clauses dataset")
    print(f"   - {len(sample_clauses)} legal clauses")
    print("   - Types: Confidentiality, Termination, Liability, Indemnification, etc.")
    print("   - Saved to: data/sample_clauses.json and data/CUAD_v1.json")
    print("\nYou can later replace with full CUAD dataset from:")
    print("https://huggingface.co/datasets/contracts/CUAD")
    
    return sample_clauses

if __name__ == "__main__":
    setup_cuad_minimal()