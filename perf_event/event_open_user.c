#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>

#define INTERVAL 5000
#define ROUND 1000

uint64_t rdtsc(void) {
	uint64_t a, d;
	__asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
	return (d<<32) | a;
}

uint64_t time[ROUND];

static long
perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags)
{
    int ret;
    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

int
main(int argc, char **argv)
{
    struct perf_event_attr pe;
    long long count;
    int fd;
    int pid = atoi(argv[1]);

    memset(&pe, 0, sizeof(struct perf_event_attr));

//  cache measurements    

    pe.type = PERF_TYPE_HW_CACHE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = (PERF_COUNT_HW_CACHE_L1D)|(PERF_COUNT_HW_CACHE_OP_WRITE << 8)|(PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16);
    pe.disabled = 1;
    pe.inherit = 1;
    pe.pinned = 1;
    pe.exclude_kernel = 0;
    pe.exclude_user = 0;
    pe.exclude_hv = 0;
    pe.exclude_host = 0;
    pe.exclude_guest = 0;


// Raw measurements
/*
    pe.type = PERF_TYPE_RAW;
    pe.config = ((MASK_CODE<<8)|(EVENT_CODE)) & 0xFFFFFF;
    pe.disabled = 1;
    pe.exclude_kernel = 0;
    pe.exclude_hv = 0;
    pe.exclude_host = 0;
    pe.exclude_guest = 0;
    pe.disabled = 0;

*/    

/*
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = PERF_COUNT_HW_INSTRUCTIONS;
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    pe.disabled = 1;
    pe.inherit = 1;
    pe.pinned = 1;
    pe.exclusive = 1;
    pe.exclude_user = 0;
    pe.exclude_kernel = 0;
    pe.exclude_hv = 0;
    pe.exclude_idle = 1;
    pe.exclude_host = 0;
    pe.exclude_guest = 0;
*/

    fd = perf_event_open(&pe, pid, -1, -1, 0);
    if (fd == -1) {
       fprintf(stderr, "Error opening leader %llx\n", pe.config);
       exit(EXIT_FAILURE);
    }

    int i;
    uint64_t start_cycle;

    for (i=0; i<ROUND; i++) {
        ioctl(fd, PERF_EVENT_IOC_RESET, 0);
        ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
	start_cycle = rdtsc();
	while(rdtsc()-start_cycle<INTERVAL);
        ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
        read(fd, &time[i], sizeof(long long));
    }

    FILE *output = fopen("data", "a");
    for (i=0; i<ROUND; i++)
        fprintf(output, "%lu\n", time[i]);
    fclose(output);

    close(fd);
}
