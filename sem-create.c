#include "xsem.h"

int
main(int argc, const char** argv)
{
    semaphore_t *semap;

    semap = semaphore_create("/tmp/semaphore");
    if (semap == NULL) return 1;
    semaphore_close(semap);
    return 0;
}
