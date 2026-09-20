#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_SZ 1024

char buf[MAX_SZ];

__attribute__((constructor)) void disable_buffering() {
  setbuf(stdin, 0);
  setbuf(stdout, 0);
  setbuf(stderr, 0);
}

void handle_open() {
  char filename[256];
  int flags;

  printf("filename: ");
  fgets(filename, sizeof(filename), stdin);
  filename[strcspn(filename, "\n")] = 0;

  printf("flags: ");
  scanf("%d", &flags);
  getchar();

  int ret = open(filename, flags);
  printf("ret = %d\n", ret);
}

void handle_seek() {
  int fd;
  long offset;
  int whence;

  printf("fd: ");
  scanf("%d", &fd);
  printf("offset: ");
  scanf("%ld", &offset);
  printf("whence: ");
  scanf("%d", &whence);
  getchar();

  long ret = lseek(fd, offset, whence);
  printf("ret = %ld\n", ret);
}

void handle_read() {
  int fd;
  int size;

  printf("fd: ");
  scanf("%d", &fd);
  printf("size: ");
  scanf("%d", &size);
  getchar();

  int ret = read(fd, buf, size);
  printf("ret = %d\n", ret);
}

void handle_write() {
  int fd;
  int size;

  printf("fd: ");
  scanf("%d", &fd);
  printf("size: ");
  scanf("%d", &size);
  getchar();

  int ret = write(fd, buf, size);
  printf("ret = %d\n", ret);
}

int main() {
  int choice;

  puts("Open Seek Read Write");
  for (;;) {
    puts("1. open");
    puts("2. seek");
    puts("3. read");
    puts("4. write");
    puts("5. exit");
    printf("> ");
    scanf("%d", &choice);
    getchar();

    switch (choice) {
    case 1:
      handle_open();
      break;
    case 2:
      handle_seek();
      break;
    case 3:
      handle_read();
      break;
    case 4:
      handle_write();
      break;
    case 5:
      exit(0);
    }
  }
}
