```
NOTE: Forked / backed up from https://github.com/dimaqq/pthread_mutexattr_init/fork
```

# IPC Synchronisation

Can 2 unrelated processes share a mutex and condition variable?

Yes they can!

GNU C library already provides the mechanism, it's documented, though not advertised.

Here are Python bindings and a practical test.

### pthread_mutexattr_init

Sample code from pthread_mutexattr_init man page, reimplemented in Python.

### System requirements:
* futex (Linux kernel)
* C library (GNU libc)
