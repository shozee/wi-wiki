#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/wait.h>

extern char **environ;

int main(int argc, char *argv[]) {
    int     pid;
    int     status;
    int     i;
    int     rc = 1;
    char  command[256];

    strcpy(command, "wiki.cgi");

    pid = fork();

    switch(pid) {
    case 0:
        /* child process */
        setgid( GID );
        setuid( UID );
        if (execve(command, argv, environ) < 0) {
            exit(EXIT_FAILURE);
        }
        break;
    case -1:
        exit(EXIT_FAILURE);
        break;
    default:
        /* parent process */
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            rc = WEXITSTATUS(status);
        }
        break;
    }

    return(rc);
}
