#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>

extern char **environ;

int main(int argc, char *argv[]) {
    int     pid;
    int     status;
    int     i;
    int     rc = 1;
    char  command[256];

    /* 実行スクリプト設定 */
    strcpy(command, "wi.sh");        // 対象スクリプトの絶対パスを設定

    pid = fork();

    switch(pid) {
    case 0:
        /* 子プロセス */
        /* スクリプト実行 */
        setgid( GID );        // setuidを設定したいuserのgid
        setuid( UID );        // setuidを設定したいuserのuid
        if (execve(command, argv, environ) < 0) {
            exit(EXIT_FAILURE);
        }
        break;
    case -1:
        /* 失敗 */
        exit(EXIT_FAILURE);
        break;
    default:
        /* 親プロセス */
        /* 子プロセスの完了を待つ */
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            rc = WEXITSTATUS(status);
        }
        break;
    }

    return(rc);
}
