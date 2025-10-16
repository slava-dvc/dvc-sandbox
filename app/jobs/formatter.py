from typing import List
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.jobs.models import Job


class JobsFormatter:
    """Formats jobs data for various output formats"""
    
    def __init__(self, jobs: List[Job]):
        self.jobs = jobs
    
    def _format_job(self, job: Job) -> str:
        """Format a single job as markdown string"""
        lines = []
        
        company_name = (job.company_name or 'Unknown Company').strip()
        title = (job.title or 'Unknown Position').strip()
        location = (job.location or 'Remote/Unknown').strip()
        
        lines.append(f"## {company_name} - {title}")
        lines.append("\n")
        lines.append(f"Location: {location}")
        
        if job.created_at:
            lines.append(f"Posted: {job.created_at.strftime('%Y-%m-%d')}")
        
        if job.updated_at:
            lines.append(f"Updated: {job.updated_at.strftime('%Y-%m-%d')}")
        
        description = job.description or 'No description available'
        lines.append(f"\n### Description:\n\n{description}")
        
        if job.job_highlights:
            lines.append("\n### Highlights:")
            for highlight in job.job_highlights:
                if highlight.title and highlight.items:
                    lines.append(f"\n#### {highlight.title}:\n")
                    for item in highlight.items:
                        lines.append(f"- {item}")
        
        if job.extensions:
            lines.append(f"\nJob Type: {', '.join(job.extensions)}")
        apply_link = None
        for apply_option in job.apply_options:
            if apply_option.title == job.via:
                apply_link = self._format_url(apply_option.link)
                break

        lines.append(f"\n## Application link\n{apply_link}")
        return '\n'.join(lines)

    def _format_url(self, url: str) -> str:
        url = urlparse(url)
        query_params = parse_qs(url.query)
        # Remove UTM parameters
        query_params = {k: v for k, v in query_params.items() if not k.startswith('utm_')}
        # Rebuild URL without UTM parameters
        return urlunparse((
            url.scheme,
            url.netloc,
            url.path,
            url.params,
            urlencode(query_params, doseq=True),
            url.fragment
        ))

    def as_markdown(self) -> str:
        """Format jobs list as markdown document"""
        if not self.jobs:
            return "# Job Opportunities\n\nNo recent job opportunities found.\n"
        
        lines = []
        lines.append("# Job Opportunities")
        lines.append(f"\n{len(self.jobs)} open roles across our portfolio companies.\n")
        
        for job in self.jobs:
            lines.append(self._format_job(job))
        
        return "\n\n---\n\n".join(lines)