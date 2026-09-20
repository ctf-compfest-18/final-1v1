#include <fcntl.h>
#include <unistd.h>

int main() {
  char buf[1024];
  int fd = open("/flag.txt", O_RDONLY);
  int size = read(fd, buf, sizeof(buf));
  write(1, buf, size);
  close(fd);
  return 0;
}
