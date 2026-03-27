SUMMARIZE_PROMPT = """You are an expert technical recruiter. Analyze the resume below and provide a structured summary in the same language as the resume content.

Include:
- Full name (if found)
- Key technical skills
- Years of experience (estimated)
- Most recent position
- Educational background
- Notable achievements

Resume content:
{content}

Provide a clear, concise summary."""


QUERY_PROMPT = """You are an expert technical recruiter. Analyze the resumes below and answer the recruiter's question with a detailed justification for each candidate.

Resumes:
{resumes}

Recruiter question: {query}

For each candidate, provide:
1. Candidate name (or filename if name not found)
2. Match assessment (Strong Match / Partial Match / No Match)
3. Justification based on specific evidence from the resume

Be objective and evidence-based."""
