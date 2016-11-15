# Fox/RenderBus cloud rendering Python API
We provides a simple Python-based API for using our cloud rendering service. This is the official API that is maintained by Fox/RenderBus RD team. The API has been tested ok with python2.7.10 and requests 2.11.1

The latest version can always be found at
https://github.com/renderbus/python-api

## Submiting Step

1. Login to our cloud server first. currently, some info like access_key need to ask us support team.
```py
fox = Fox(render_server="www5.renderbus.com", account="XXX", access_key="XXX", aspera_server="app5.renderbus.com", aspera_password="XXX")
```

- Upload local files to cloud server, skip exists same files by default, you can upload the files and folders.
```py
fox.upload(path_list=[r"v:\project\shot\lgt.ma", r"v:\project\asset\sourceimages])
```

- After all the dependancy files of Maya file has been uploaded, you can submit task to cloud server.
```py
fox.submit_task(project_name="XXX", input_scene_path=r"v:\project\shot\lgt.ma", frames="1-10[1]") ```

- After render complete, you can download the entire task output files from cloud server, and single frame output files downloading is not supported yet currently. The download method would skip exists same files which already downloaded by default
```py
fox.download(task_id=11111, local_path=r"v:\project\output")
```

## Query method
 - get user info
```py
fox.get_users()
```

- get all projects
```py
fox.get_projects()
```

- get specific project info
```py
fox.get_projects(project_name="XXX")
```

- get all tasks
```py
fox.get_tasks()
```

- get all tasks of specific project
```py
fox.get_tasks(project_name="XXX")
```

- get specific task
```py
fox.get_tasks(task_id=11111)
```

- get specific task with frames info
```py
fox.get_tasks(task_id=11111, has_frames=1)
```
