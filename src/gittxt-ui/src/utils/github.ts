export function parseGitHubURL(input) {
    try {
      const url = new URL(input);
      if (!url.hostname.includes('github.com')) return { repo: null };
  
      const [, owner, name, tree, branch] = url.pathname.split('/');
      const repo = `${owner}/${name}`;
      return { repo, branch };
    } catch {
      return { repo: null };
    }
  }
  