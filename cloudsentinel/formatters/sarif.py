# cloudsentinel/formatters/sarif.py
def generate_sarif(findings: list, file_path: str = "infrastructure.json") -> dict:
    """
    Converts CloudSentinel findings into the industry-standard SARIF format.
    """
    results = []
    for finding in findings:
        results.append({
            "ruleId": finding.get("rule", "unknown"),
            "message": {"text": finding.get("description", "No description provided")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": file_path},
                    # Defaulting to line 1 if the core engine doesn't emit line numbers yet
                    "region": {"startLine": finding.get("line", 1)}
                }
            }]
        })
        
    sarif_output = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "CloudSentinel",
                    "informationUri": "https://github.com/rakshitcodesx/cloudsentinel",
                    "version": "1.0.0"
                }
            },
            "results": results
        }]
    }
    return sarif_output
