from flask import Flask, render_template, request, send_file, jsonify
from src.gittxt.scanner import Scanner
from src.gittxt.repository import RepositoryHandler
from src.gittxt.output_builder import OutputBuilder
from src.gittxt.config import ConfigManager
from .forms import ScanForm
import os

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

        # Handle repository
        repo_handler = RepositoryHandler(repo_source)
        repo_path = repo_handler.get_local_path()
        
        if not repo_path:
            return render_template('index.html', form=form, error="Failed to access repository")

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
            return render_template('index.html', form=form, error="No valid files found for extraction")

        # Generate output
        repo_name = os.path.basename(os.path.normpath(repo_path))
        builder = OutputBuilder(
            repo_name=repo_name,
            output_format=output_format
        )

        # Collect summary statistics
        total_size = sum(os.path.getsize(f) for f in valid_files)
        file_types = {os.path.splitext(f)[1] for f in valid_files}
        summary_data = {
            "total_files": len(valid_files),
            "total_size": total_size,
            "file_types": list(file_types)
        }

        # Generate outputs
        output_files = builder.generate_output(valid_files, repo_path, summary_data)
        
        return render_template(
            'results.html',
            summary=summary_data,
            output_files=output_files,
            tree_summary=tree_summary
        )

    return render_template('index.html', form=form)

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

def create_app():
    return app
