#!/usr/bin/env python
import sys
from crew import AntigravityCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'user_request': 'Xây dựng một ứng dụng quản lý công việc (To-Do App) có tính năng đăng nhập, tạo task, kéo thả task giữa các cột status.'
    }
    AntigravityCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()
