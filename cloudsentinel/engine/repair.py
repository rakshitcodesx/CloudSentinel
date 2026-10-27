import os
import tempfile
import ollama
from server import scan_infrastructure

def generate_and_verify_fix(file_path: str, finding: dict, model_name: str = "codellama") -> dict:
    """
    Asks a local LLM to fix a specific security finding, then verifies the fix using the Cedar engine.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        original_content = f.read()
        
    prompt = (
        f"Fix this Infrastructure-as-Code file to resolve the following policy violation:\n"
        f"Rule: {finding.get('rule')}\n"
        f"Description: {finding.get('description')}\n\n"
        f"Code:\n{original_content}\n\n"
        f"Output ONLY the fixed raw code. Do not include markdown code blocks, backticks, or explanations."
    )
    
    try:
        response = ollama.generate(model=model_name, prompt=prompt)
        candidate_fix = response.get("response", "").strip()
        
        # Clean up markdown if the LLM hallucinated code block syntax
        if candidate_fix.startswith("```"):
            lines = candidate_fix.split("\n")
            candidate_fix = "\n".join(lines[1:-1]).strip()
            
        # Write to a temporary file to run through the existing scan_infrastructure tool
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(candidate_fix.encode('utf-8'))
            temp_path = temp_file.name
            
        verify_result = scan_infrastructure(temp_path)
        os.remove(temp_path)
        
        # Check if the specific finding was successfully removed by the LLM
        still_failing = any(f.get('rule') == finding.get('rule') for f in verify_result.get("findings", []))
        
        return {
            "success": not still_failing,
            "candidate_content": candidate_fix,
            "verification_scan": verify_result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
