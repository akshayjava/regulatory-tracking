import os
import time
import subprocess
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False
        self.task_manager = TaskManager()

    def start(self):
        self.running = True
        logger.info("Starting Agent Manager Loop...")

        # Core continuous improvement loop
        self.scheduler.add_job(self.run_cycle, 'interval', minutes=5)

        # Scheduled checks
        self.scheduler.add_job(self.check_health, 'interval', minutes=15)
        self.scheduler.add_job(self.run_tests, 'cron', hour=2)
        self.scheduler.add_job(self.auto_update_dependencies, 'cron', day_of_week='sun', hour=3)

        self.scheduler.start()

        try:
            # Keep main thread alive and monitor tasks
            while self.running:
                self.task_manager.process_pending_tasks()
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def stop(self):
        self.running = False
        self.scheduler.shutdown()
        logger.info("Agent Manager stopped.")

    def run_cycle(self):
        """Continuous evaluation and generation of tasks."""
        logger.info("Running continuous improvement cycle...")
        # 1. Analyze logs and current state to identify issues
        issues = self._analyze_system_state()
        for issue in issues:
            self.task_manager.add_task(f"Debug and Fix: {issue['summary']}", "debug", issue)

        # 2. Check for missing tests or refactoring opportunities
        improvements = self._find_improvement_opportunities()
        for imp in improvements:
             self.task_manager.add_task(f"Upgrade/Refactor: {imp['summary']}", "upgrade", imp)

    def _analyze_system_state(self) -> List[Dict[str, Any]]:
        issues = []
        try:
            # Check for python syntax errors using py_compile on backend files
            import glob
            for file in glob.glob("backend/**/*.py", recursive=True):
                try:
                    import py_compile
                    py_compile.compile(file, doraise=True)
                except py_compile.PyCompileError as e:
                    issues.append({"summary": f"Syntax error in {file}", "details": str(e)})
        except Exception as e:
            logger.error(f"Error analyzing state: {e}")
        return issues

    def _find_improvement_opportunities(self) -> List[Dict[str, Any]]:
        improvements = []
        try:
            # Check if there are no tests for a python module
            import glob
            for file in glob.glob("backend/**/*.py", recursive=True):
                if "tests" not in file and "agent_manager" not in file:
                    filename = os.path.basename(file)
                    test_file = f"backend/tests/test_{filename}"
                    if not os.path.exists(test_file):
                        improvements.append({"summary": f"Missing tests for {filename}", "file": file})
        except Exception as e:
            logger.error(f"Error finding improvements: {e}")
        return improvements

    def check_health(self):
        logger.info("Checking system health...")
        # Add actual health checks (API responsiveness, DB connection)
        pass

    def run_tests(self):
        logger.info("Running automated tests...")
        try:
            if os.path.exists('backend/tests'):
                subprocess.run(['pytest', 'backend/tests/'], check=True, capture_output=True)
                logger.info("Tests passed successfully.")
            else:
                logger.warning("No tests found to run.")
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode('utf-8')
            logger.error(f"Tests failed.")
            self.task_manager.add_task("Fix Failing Tests", "debug", {"error": error_output})

    def auto_update_dependencies(self):
        logger.info("Checking for dependency updates...")
        self.task_manager.add_task("Update Dependencies", "upgrade", {})

class Task(BaseModel):
    id: str
    description: str
    type: str # e.g., 'debug', 'upgrade', 'feature'
    context: Dict[str, Any]
    status: str = 'pending' # 'pending', 'in_progress', 'completed', 'failed'

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, description: str, task_type: str, context: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, description=description, type=task_type, context=context)
        self.tasks.append(task)
        logger.info(f"Added task [{task_id}]: {description}")
        return task_id

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.status == 'pending']

    def process_pending_tasks(self):
        pending = self.get_pending_tasks()
        for task in pending:
            self._execute_task(task)

    def _execute_task(self, task: Task):
        logger.info(f"Executing task [{task.id}]: {task.description}")
        task.status = 'in_progress'

        # Here we delegate to the appropriate sub-agent based on task type
        sub_agent = SubAgent(role=task.type)
        success = sub_agent.execute(task)

        if success:
            task.status = 'completed'
            logger.info(f"Task [{task.id}] completed successfully.")
        else:
            task.status = 'failed'
            logger.error(f"Task [{task.id}] failed.")

class SubAgent:
    def __init__(self, role: str):
        self.role = role
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
            else:
                self.client = None
                logger.warning("No ANTHROPIC_API_KEY found. SubAgent will use mock execution.")
        except ImportError:
            self.client = None
            logger.warning("anthropic package not found. SubAgent will use mock execution.")

    def execute(self, task: Task) -> bool:
        """
        Executes the task. Sends the task context to an LLM if available and executes the suggested bash/python commands.
        """
        logger.info(f"SubAgent [{self.role}] starting work on task [{task.id}]...")

        try:
            if self.role == 'debug':
                return self._handle_debug(task)
            elif self.role == 'upgrade':
                return self._handle_upgrade(task)
            else:
                logger.warning(f"Unknown sub-agent role: {self.role}")
                return False
        except Exception as e:
            logger.error(f"SubAgent error: {str(e)}")
            return False

    def _ask_llm(self, prompt: str) -> str:
        if self.client:
            try:
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    system="You are an autonomous sub-agent helping debug and upgrade a codebase. Output only the command to run or code to change without formatting.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Error querying LLM: {str(e)}")
                return ""
        else:
            return ""

    def _handle_debug(self, task: Task) -> bool:
        logger.info(f"Analyzing logs and applying fix for: {task.description}")

        if self.client:
             prompt = f"You are an assistant. I need to fix: {task.description}. Suggest a command or python script that fixes this issue based on the context: {json.dumps(task.context)}."
             response = self._ask_llm(prompt)
             if response:
                  logger.info(f"LLM suggested fix: {response}")
                  logger.info("Approval required to execute. Simulation mode enabled.")
             else:
                  logger.info("No actionable fix suggested by LLM.")
                  return False
        return True

    def _handle_upgrade(self, task: Task) -> bool:
        logger.info(f"Reviewing codebase and refactoring for: {task.description}")

        if self.client:
             prompt = f"You are an assistant. I need to upgrade or refactor: {task.description}. Suggest a command or python script that implements this upgrade based on the context: {json.dumps(task.context)}."
             response = self._ask_llm(prompt)
             if response:
                  logger.info(f"LLM suggested upgrade: {response}")
                  logger.info("Approval required to execute. Simulation mode enabled.")
             else:
                  logger.info("No actionable upgrade suggested by LLM.")
                  return False
        return True

if __name__ == "__main__":
    manager = AgentManager()
    # Adding an initial task for demonstration
    manager.task_manager.add_task("Initial project review", "upgrade", {})
    manager.start()
