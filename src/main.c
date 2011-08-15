#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>

int main(int argc, char* argv[]) 
{
    char* tar_argv[5];
    tar_argv[0] = "tar";
    tar_argv[1] = "cjf";
    tar_argv[2] = "a.bz2";
    tar_argv[3] = "main.c";
    tar_argv[4] = 0;

    pid_t pid;
    if ((pid = fork()) < 0)
    {
	exit(-1);
    }
    else if (pid == 0)
    {
	int ret = execvp("tar", tar_argv);
	exit(ret);
    }

    int ret = 0;
    waitpid(pid, &ret, 0);
    printf("result %d\n", ret);

    return 0;
}
