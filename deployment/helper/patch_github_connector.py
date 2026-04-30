import sys

with open("deployment/onyx/github_connector.py.orig", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("from collections.abc import Generator"):
        new_lines.append(line)
        new_lines.append("from collections import deque\n")
    elif "PRS = \"prs\"" in line:
        new_lines.append(line)
        new_lines.append("    FILES = \"files\"\n")
    elif "cursor_url: str | None = None" in line:
        new_lines.append(line)
        new_lines.append("    file_queue: list[str] | None = None\n")
    elif "self.cursor_url = None" in line:
        new_lines.append(line)
        new_lines.append("        self.file_queue = None\n")
    elif "include_issues: bool = False," in line:
        new_lines.append(line)
        new_lines.append("        include_code_files: bool = False,\n")
        new_lines.append("        include_files_md: bool = False,\n")
    elif "self.include_issues = include_issues" in line:
        new_lines.append(line)
        new_lines.append("        self.include_code_files = include_code_files\n")
        new_lines.append("        self.include_files_md = include_files_md\n")
    elif "checkpoint.stage = GithubConnectorStage.PRS" in line and "ISSUES" in "".join(new_lines[-20:]):
        new_lines.append(line.replace("PRS", "FILES"))
    elif "def _convert_issue_to_document(" in line:
        # Insert _convert_github_file_to_document before _convert_issue_to_document
        new_lines.append("""
def _convert_github_file_to_document(
    repo: Repository.Repository, 
    content_file: Any, 
    repo_external_access: ExternalAccess | None
) -> Document:
    repo_full_name = repo.full_name
    parts = repo_full_name.split("/", 1)
    owner_name = parts[0] if parts else ""
    repo_name = parts[1] if len(parts) > 1 else repo_full_name

    try:
        content = content_file.decoded_content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = content_file.decoded_content.decode("latin-1")
        except Exception:
            content = ""
    except Exception:
        content = ""

    doc_metadata = {
        "repo": repo_full_name,
        "hierarchy": {
            "source_path": [owner_name, repo_name, "files"] + content_file.path.split("/"),
            "owner": owner_name,
            "repo": repo_name,
            "object_type": "file",
        },
    }

    return Document(
        id=content_file.html_url,
        sections=[TextSection(link=content_file.html_url, text=content)],
        source=DocumentSource.GITHUB,
        external_access=repo_external_access,
        semantic_identifier=content_file.name,
        doc_updated_at=datetime.now(timezone.utc),
        doc_metadata=doc_metadata,
        metadata={
            "object_type": "CodeFile",
            "repo": repo_full_name,
            "path": content_file.path,
        },
    )

""")
        new_lines.append(line)
    elif "checkpoint.stage = GithubConnectorStage.PRS" in line and "ISSUES" in "".join(new_lines[-10:]):
         new_lines.append("            checkpoint.stage = GithubConnectorStage.FILES\n")
    elif "checkpoint.reset()" in line and "FILES" in "".join(new_lines[-5:]):
        new_lines.append(line)
        # Add the FILES stage logic
        new_lines.append("""
        if (self.include_code_files or self.include_files_md) and checkpoint.stage == GithubConnectorStage.FILES:
            logger.info(f"Fetching files for repo: {repo.name}")
            if checkpoint.file_queue is None:
                checkpoint.file_queue = [""]
            
            num_files = 0
            while checkpoint.file_queue:
                current_path = checkpoint.file_queue.pop(0)
                try:
                    contents = repo.get_contents(current_path)
                    if not isinstance(contents, list):
                        contents = [contents]
                    
                    for content_file in contents:
                        if content_file.type == "dir":
                            checkpoint.file_queue.append(content_file.path)
                        elif content_file.type == "file":
                            is_md = content_file.name.lower().endswith(".md")
                            is_code = any(content_file.name.lower().endswith(ext) for ext in [
                                ".py", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".hpp", ".java", 
                                ".rb", ".php", ".rs", ".sh", ".yaml", ".yml", ".json", ".sql",
                                ".html", ".css", ".tsx", ".jsx", ".mdx"
                            ])
                            
                            if (is_md and self.include_files_md) or (is_code and self.include_code_files):
                                try:
                                    if is_slim:
                                        yield Document(
                                            id=content_file.html_url,
                                            sections=[],
                                            external_access=repo_external_access,
                                            source=DocumentSource.GITHUB,
                                            semantic_identifier="",
                                            metadata={},
                                        )
                                    else:
                                        doc = _convert_github_file_to_document(repo, content_file, repo_external_access)
                                        yield doc
                                    
                                    num_files += 1
                                except Exception as e:
                                    logger.exception(f"Error converting file {content_file.path}: {e}")
                except Exception as e:
                    logger.exception(f"Error fetching contents for {current_path}: {e}")
            
            logger.info(f"Fetched {num_files} files for repo: {repo.name}")
            checkpoint.stage = GithubConnectorStage.PRS
            checkpoint.reset()
""")
    else:
        new_lines.append(line)

with open("deployment/onyx/github_connector.py", "w") as f:
    f.writelines(new_lines)
