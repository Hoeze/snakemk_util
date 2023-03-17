rule pythonrule:
  input:
    t1=f'{config["testdir_name"]}/out.txt',
    t2=[
        f'{config["testdir_name"]}/out.txt',
        f'{config["testdir_name"]}/out.txt',
    ],
  output:
    of=touch(f'{config["testdir_name"]}/python.done')
  input:
  script:
      print("all fine")