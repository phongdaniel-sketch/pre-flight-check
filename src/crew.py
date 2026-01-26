from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class AntigravityCrew():
	"""AntigravityCrew crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def pm(self) -> Agent:
		return Agent(
			config=self.agents_config['pm'],
			verbose=True,
			allow_delegation=True
		)

	@agent
	def ba(self) -> Agent:
		return Agent(
			config=self.agents_config['ba'],
			verbose=True
		)

	@agent
	def ui_ux(self) -> Agent:
		return Agent(
			config=self.agents_config['ui_ux'],
			verbose=True
		)

	@agent
	def senior_be(self) -> Agent:
		return Agent(
			config=self.agents_config['senior_be'],
			verbose=True
		)

	@agent
	def senior_fe(self) -> Agent:
		return Agent(
			config=self.agents_config['senior_fe'],
			verbose=True
		)

	@agent
	def qa(self) -> Agent:
		return Agent(
			config=self.agents_config['qa'],
			verbose=True
		)

	@agent
	def devops(self) -> Agent:
		return Agent(
			config=self.agents_config['devops'],
			verbose=True
		)

	@task
	def sprint1_planning(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_planning'],
		)

	@task
	def sprint1_design(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_design'],
		)

	@task
	def sprint1_backend(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_backend'],
		)

	@task
	def sprint1_frontend(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_frontend'],
		)

	@task
	def sprint1_qa(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_qa'],
		)

	@task
	def sprint1_release(self) -> Task:
		return Task(
			config=self.tasks_config['sprint1_release'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AntigravityCrew crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks,   # Automatically created by the @task decorator
			process=Process.hierarchical,
			manager_agent=self.pm(), # PM is the manager
			verbose=True,
		)
