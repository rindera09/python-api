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
fox = Fox(render_server="www5.renderbus.com", account="XXX", access_key="XXX")
```

- Upload local files or folders to cloud server and skip the existing same file by default.
```py
fox.upload(path_list=[r"v:\project\shot\lgt.ma", r"v:\project\asset\sourceimages"])
```

- Create the project
```py
fox.create_project(project_name="XXX")
```

- Add the plugins setting for project
```py
fox.add_project_config(10000, "maya 2014", "pgYetiMaya 1.3.17")
```

- After all the dependancy files of Maya Task such as texture, cache etc have been uploaded, you can submit task to cloud server.
```py
fox.submit_task(project_name="XXX", input_scene_path=r"v:\project\shot\lgt.ma", frames="1-10[1]")
```

- You can also try below method to add some extra info to submit the task.
```py
task_info = {"project_name": "api",
               "input_scene_path": r"E:\test_files\2014_api_camera_layer.mb",
               "frames": "1073-1073[1]",
               "render_layer": "ball",
               "camera": "camera1"}
fox.submit_task(**task_info)
```

- After rendering complete, you can download the entire task output files from cloud server, but single frame download function is not supported yet. The download method will skip the existing same files which already downloaded by default.
```py
fox.download(task_id=11111, local_path=r"v:\project\output")
```

## Query Method
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

- get task using task filter
```py
task_filter={"project_name": "XXX", "task_status": "Start"}
task_filter={"project_name": "XXX", "task_status": "System_Done"}
fox.get_tasks(task_filter=task_filter)
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

## Some operate plugins configuration for project

- get the software and plugin configuration for project that support by rayvision
```py
fox.get_plugins_available()
```

- add the software and plugin configuration for project
```py
fox.add_project_config(project_id=10000, cg_soft_name="maya 2014", plugin_name="pgYetiMaya 1.3.17", is_default=0)
```

- delete software and plugin configuration for project
```py
fox.delete_project_config(project_id=12345, config_id=45678)
```
(you can use "get_project_info" to get config_id)

- modify the software and plugin configuration for project
```py
fox.modify_project_config(project_id=12345, config_id=23456, cg_soft_name="maya 2014", plugin_name="pgYetiMaya 1.3.17", is_default=1)
```

## Some operation of task

- submit_task()
- get_tasks()

- stop the task

```py
fox.stop_tasks(task_id=23456)
```

- delete the task

```py 
fox.delete_tasks(task_id=12345)
```

- restart the task

```py
fox.restart_tasks(task_id=12345, restart_type=1)
```

restart_type:  

0 -- restart the failed frames
               
1 -- restart the frames that give up

2 -- restart the finished frames 

3 -- restart the start frames

4 -- restart the waiting frames 


## HTTP API Manual
Generally, This is not necessary to see this manual, but if you like you can find the latest version HTTP API Manual at https://innerx.gitbooks.io/rayvision-render-api/content/, we only have a chinese version of manual currently.
