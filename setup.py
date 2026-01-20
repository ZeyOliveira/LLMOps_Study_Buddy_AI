from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="llmops-gitops-study-buddy-ai",
    version="0.1.0",
    author="Zey Oliveira",
    description="End-to-end LLMOps GitOps pipeline for study buddy AI application",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.12",
)
