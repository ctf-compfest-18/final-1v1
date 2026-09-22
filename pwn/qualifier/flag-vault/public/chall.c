#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdint.h>

#define FLAG_MAX_LEN 0x30
#define PASSWORD_BYTES 0x10
#define PASSWORD_LEN (PASSWORD_BYTES * 2)

char *flag;
char **password_ref;

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    flag = malloc(FLAG_MAX_LEN);
    if (flag == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    int fd = open("flag.txt", O_RDONLY);
    if (fd < 0) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    ssize_t n = read(fd, flag, FLAG_MAX_LEN);
    if (n <= 0) {
        perror("read");
        exit(EXIT_FAILURE);
    }
    flag[strcspn(flag, "\n")] = '\0';
    close(fd);

    char *generated_password = malloc(PASSWORD_LEN + 1);
    password_ref = malloc(0x40);
    if (generated_password == NULL || password_ref == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    unsigned char random_bytes[PASSWORD_BYTES];
    n = read(fd, random_bytes, PASSWORD_BYTES);
    if (n != PASSWORD_BYTES) {
        perror("read");
        exit(EXIT_FAILURE);
    }
    close(fd);

    for (size_t i = 0; i < PASSWORD_BYTES; i++) {
        snprintf(generated_password + (i * 2), 3, "%02x", random_bytes[i]);
    }
    generated_password[PASSWORD_LEN] = '\0';
    *password_ref = generated_password;
}

int main(void) {
    init();

    char *buf = malloc(0x40);
    char *retry_note = malloc(0x40);
    char *audit_note = malloc(0x40);
    if (buf == NULL || retry_note == NULL || audit_note == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    __printf_chk(1, "What's the password?\n");
    if (read(STDIN_FILENO, buf, 0x40) <= 0) {
        return 0;
    }
    buf[strcspn(buf, "\n")] = '\0';
    snprintf(retry_note, 0x40, "retry available for %.24s", buf);
    snprintf(audit_note, 0x40, "failed login: %.24s", buf);

    if (memcmp(buf, *password_ref, PASSWORD_LEN) == 0) {
        __printf_chk(1, "Congrats! %s\n", flag);
        return 0;
    }

    free(audit_note);
    free(retry_note);

    __printf_chk(1, "Incorrect password: ");
    __printf_chk(1, buf, buf);
    __printf_chk(1, "\n");

    __printf_chk(1, "Try harder:\n");
    if (read(STDIN_FILENO, buf, 0x58) <= 0) {
        return 0;
    }

    char *retry_record = malloc(0x40);
    char *reset_request = malloc(0x40);
    if (retry_record == NULL || reset_request == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    __printf_chk(1, "Reset password:\n");
    if (read(STDIN_FILENO, reset_request, sizeof(password_ref)) <= 0) {
        return 0;
    }

    __printf_chk(1, "Try again:\n");
    if (read(STDIN_FILENO, buf, 0x40) <= 0) {
        return 0;
    }
    buf[strcspn(buf, "\n")] = '\0';

    if (memcmp(buf, *password_ref, PASSWORD_LEN) == 0) {
        __printf_chk(1, "Congrats! %s\n", flag);
    }

    return 0;
}
