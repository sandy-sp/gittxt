import os
from flask import Flask, render_template, request, send_file, jsonify, url_for
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder
from gittxt.config import ConfigManager
from .forms import ScanForm
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
config = ConfigManager.load_config()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScanForm()
    if form.validate_on_submit():
        # Get form data
        repo_source = form.repo_url.data
        output_format = ','.join(form.output_format.data)
        include_patterns = form.include_patterns.data
        exclude_patterns = form.exclude_patterns.data
        size_limit = form.size_limit.data
        docs_only = form.docs_only.data
        auto_filter = form.auto_filter.data

        try:
            # Handle repository
            repo_handler = RepositoryHandler(repo_source)
            repo_path = repo_handler.get_local_path()
            
            if not repo_path:
                return render_template('index.html', form=form, error="Failed to access repository. Please check the URL or path.")

            # Initialize scanner
            scanner = Scanner(
                root_path=repo_path,
                include_patterns=include_patterns.split(',') if include_patterns else None,
                exclude_patterns=exclude_patterns.split(',') if exclude_patterns else None,
                size_limit=size_limit,
                docs_only=docs_only,
                auto_filter=auto_filter
            )

            # Scan repository
            valid_files, tree_summary = scanner.scan_directory()
            if not valid_files:
                return render_template('index.html', form=form, error="No valid files found for extraction. Try adjusting your filters.")

            # Generate output
            repo_name = os.path.basename(os.path.normpath(repo_path))
            builder = OutputBuilder(
                repo_name=repo_name,
                output_format=output_format
            )

            # Collect summary statistics
            total_size = sum(os.path.getsize(f) for f in valid_files)
            file_types = {os.path.splitext(f)[1] for f in valid_files}
            
            # Estimate token count (rough approximation)
            total_chars = 0
            for file_path in valid_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_chars += len(f.read())
                except:
                    pass
            
            estimated_tokens = int(total_chars / 4)  # Rough estimate: 4 chars per token
            
            summary_data = {
                "total_files": len(valid_files),
                "total_size": total_size,
                "file_types": sorted(list(file_types)),
                "estimated_tokens": estimated_tokens,
                "scan_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "repo_name": repo_name
            }

            # Generate outputs
            output_files = builder.generate_output(valid_files, repo_path, summary_data)
            
            # Get file sizes for display
            file_sizes = {}
            for file_path in output_files:
                try:
                    file_sizes[file_path] = os.path.getsize(file_path)
                except:
                    file_sizes[file_path] = 0
            
            return render_template(
                'results.html',
                summary=summary_data,
                output_files=output_files,
                tree_summary=tree_summary,
                file_sizes=file_sizes,
                os=os  # Pass os module to template for file operations
            )
        except Exception as e:
            return render_template('index.html', form=form, error=f"An error occurred: {str(e)}")

    return render_template('index.html', form=form)

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/preview-repo')
def preview_repo():
    repo_source = request.args.get('repo')
    if not repo_source:
        return jsonify({"error": "No repository URL or path provided"}), 400
    
    try:
        # Handle repository
        repo_handler = RepositoryHandler(repo_source)
        repo_path = repo_handler.get_local_path()
        
        if not repo_path:
            return jsonify({"error": "Failed to access repository"}), 400
        
        # Get repository name
        repo_name = os.path.basename(os.path.normpath(repo_path))
        
        # Generate tree structure (limited depth for preview)
        scanner = Scanner(root_path=repo_path, auto_filter=True)
        _, tree_summary = scanner.scan_directory(preview_mode=True)
        
        return jsonify({
            "repo_name": repo_name,
            "tree": tree_summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/preview-file')
def preview_file():
    file_path = request.args.get('path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    try:
        # Determine language for syntax highlighting
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'plaintext',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.go': 'go',
            '.ts': 'typescript',
            '.sh': 'bash',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
        }
        language = language_map.get(ext, 'plaintext')
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Limit content size for preview
            if len(content) > 100000:  # ~100KB limit
                content = content[:100000] + "\n\n... (file truncated for preview) ..."
        
        return jsonify({
            "content": content,
            "language": language
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_app():
    return app
