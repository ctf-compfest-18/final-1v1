#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
  char flag[64] = {0};
  char input[256];

  setbuf(stdout, NULL);

  int fd = open("flag.txt", O_RDONLY);
  if (fd < 0) {
    puts("failed to open flag.txt");
    return 1;
  }

  read(fd, flag, sizeof(flag) - 1);
  close(fd);

  printf("input: ");
  fgets(input, sizeof(input), stdin);
  printf(input);

  return 0;
}
