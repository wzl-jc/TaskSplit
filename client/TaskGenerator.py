import time


class TaskGenerator(object):
    def __init__(self, split_app_info, scheduler_app_info):
        self.split_app_info = split_app_info
        self.scheduler_app_info = scheduler_app_info
        self.frame_num = 0
        self.cold_boot_num = 5

    def get_cold_boot_task(self, frame):
        pass

    def get_task_list(self, frame):
        self.frame_num += 1
        task_list = []
        task = {
            "id": self.frame_num,
            "t_init": time.time(),
            "cur_step": 0,
            "task_name": self.scheduler_app_info["flow"][0]["name"],
            "input_ctx": {
                "image": frame,
            }
        }
        task_list.append(task)
        return task_list

