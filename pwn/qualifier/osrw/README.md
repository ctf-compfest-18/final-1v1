# OSRW

author: kannrisha

## Description

open seek read write

## Flag

`COMPFEST18{eb37f09e50ef8af462680076}`

## Additional Hints

- Ever heard of `/proc/<pid>/mem`?
- open("/proc/self/mem", O_RDWR) -> lseek(<proc_self_mem_fd>, <main_addr>, SEEK_SET) -> read(0, buf, 1000), fill it with nopsled padded shellcode to execve(/bin/sh, NULL, NULL) -> write(<proc_self_mem_fd>, buf, 1000)

## Password

2535dd55c2b5df259ecf39d3
