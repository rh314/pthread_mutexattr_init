import os
import mmap
import cffi
import contextlib

ffi = cffi.FFI()
ffi.cdef("""
typedef struct __pthread_mutexattr_t {long long x;} pthread_mutexattr_t;  // either 4 or 8 bytes per header file
int pthread_mutexattr_init(pthread_mutexattr_t *attr);
int pthread_mutexattr_setpshared(pthread_mutexattr_t *attr, int pshared);

typedef struct __pthread_condattr_t {long long x;} pthread_condattr_t;  // either 4 or 8 bytes per header file
int pthread_condattr_init(pthread_condattr_t *attr);
int pthread_condattr_setpshared(pthread_condattr_t *attr, int pshared);

typedef struct __pthread_mutex_t pthread_mutex_t;  // actually 40 bytes
int pthread_mutex_init(pthread_mutex_t *restrict mutex, const pthread_mutexattr_t *restrict attr);
int pthread_mutex_lock(pthread_mutex_t *mutex);
int pthread_mutex_trylock(pthread_mutex_t *mutex);
int pthread_mutex_unlock(pthread_mutex_t *mutex);

typedef struct __pthread_cond_t pthread_cond_t;  // actually 48 bytes
int pthread_cond_init(pthread_cond_t *restrict cond, const pthread_condattr_t *restrict attr);
int pthread_cond_signal(pthread_cond_t *cond);
// int pthread_cond_timedwait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex, const struct timespec *restrict abstime);
int pthread_cond_wait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex);
""")

C = ffi.dlopen(None)

# FIXME make atomic using renameat2 or hard links
if os.path.exists("/tmp/semaphore"):
    with open("/tmp/semaphore", "rb+") as f:
        m = mmap.mmap(f.fileno(), 0)  # default: all file, share, read-write

    data = ffi.cast("unsigned long[3]", id(m))[2]  # pointer to mapped area, 64-bit CPython
    lock = ffi.cast("pthread_mutex_t *", data)
    cond = ffi.cast("pthread_cond_t *", data + 40)
else:
    l = ffi.new("pthread_mutexattr_t *")
    assert not C.pthread_mutexattr_init(l)
    assert not C.pthread_mutexattr_setpshared(l, 1)  # PTHREAD_PROCESS_SHARED

    c = ffi.new("pthread_condattr_t *")
    assert not C.pthread_condattr_init(c)
    assert not C.pthread_condattr_setpshared(c, 1)  # PTHREAD_PROCESS_SHARED

    # lock is 40 bytes, condition is 48 bytes
    # steal mmap's data pointer
    # with open("/tmp/semaphore", "rb+") as f:
    with open("/tmp/semaphore", "xb+") as f:
        f.truncate(0)
        f.write(b"\0" * 1024)  # 40 byte lock, 48 byte condition variable, rest is shared data
        f.flush()
        m = mmap.mmap(f.fileno(), 0)  # default: all file, share, read-write

    data = ffi.cast("unsigned long[3]", id(m))[2]  # pointer to mapped area, 64-bit CPython
    lock = ffi.cast("pthread_mutex_t *", data)
    cond = ffi.cast("pthread_cond_t *", data + 40)

    assert not C.pthread_mutex_init(lock, l)
    assert not C.pthread_cond_init(cond, c)

    del l, c


@contextlib.contextmanager
def locked(alock):
    assert not C.pthread_mutex_lock(alock)
    try:
        yield
    finally:
        assert not C.pthread_mutex_unlock(alock)

import sys
if "wait" in sys.argv:
    with locked(lock):
        assert not C.pthread_cond_wait(cond, lock)
elif "signal" in sys.argv:
    with locked(lock):
        assert not C.pthread_cond_signal(cond)
