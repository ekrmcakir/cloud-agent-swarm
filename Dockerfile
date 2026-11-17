# Multi-stage production container for CloudAgentSwarm
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS runtime

# Run as non-root user for enterprise zero-trust
RUN useradd -u 10001 -m swarmuser
WORKDIR /home/swarmuser/app

COPY --from=builder /root/.local /home/swarmuser/.local
COPY src/ ./src/
COPY pyproject.toml ./

ENV PATH=/home/swarmuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
USER 10001

ENTRYPOINT ["python", "-m", "cloud_agent_swarm.cli.main"]
CMD ["simulate", "--scenario", "oom_cascade"]
