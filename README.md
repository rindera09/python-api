# Fox Render Farm / Renderbus cloud rendering Python API
We provide a simple Python-based API for using our cloud rendering service. This is the official API that is maintained by Fox Render Farm / Renderbus RD team. The API has been tested ok with python2.7.10 and requests 2.11.1

The latest version can always be found at
https://github.com/renderbus/python-api

## Requirement
- requests (We already test ok with requests 2.11.1)

## Submiting Step
- You must have a Fox Render Farm / Renderbus account to use our service, then create a project and select the plugins you want to use on our web site before submiting.

- Login in our cloud server account first, some information such as access key, you need ask for our support team.
```py
fox = Fox(render_server="www5.renderbus.com", account="XXX", access_key="XXX", aspera_server="app5.renderbus.com", aspera_password="XXX")
```

- Upload local files or folders to cloud server and skip the existing same file by default.
```py
fox.upload(path_list=[r"v:\project\shot\lgt.ma", r"v:\project\asset\sourceimages"])
```

- After all the dependancy files of Maya Task such as texture, cache etc have been uploaded, you can submit task to cloud server.
```py
fox.submit_task(project_name="XXX", input_scene_path=r"v:\project\shot\lgt.ma", frames="1-10[1]")
```

- After rendering complete, you can download the entire task output files from cloud server, but single frame download function is not supported yet. The download method will skip the existing same files which already downloaded by default.
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
