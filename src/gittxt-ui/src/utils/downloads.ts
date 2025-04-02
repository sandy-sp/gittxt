export function downloadFile(type, url) {
    const link = document.createElement('a');
    link.href = url;
    link.download = `gittxt_output.${type}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  