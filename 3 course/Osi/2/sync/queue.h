#ifndef __FITOS_QUEUE_H__
#define __FITOS_QUEUE_H__

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <semaphore.h>
#include <unistd.h>

typedef struct _QueueNode {
	int val;
	struct _QueueNode *next;
} qnode_t;

typedef struct _Queue {
	qnode_t *first;
	qnode_t *last;

	pthread_t qmonitor_tid;
	pthread_spinlock_t spinlock;
	pthread_mutex_t mutex;
	pthread_cond_t cond;
	// sem_t sem;
	sem_t is_not_full;
	sem_t is_not_empty;
	sem_t statistic_sem;



	int count;
	int max_count;

	// queue statistics

	double get_avg_time;
	double add_avg_time;
	long add_attempts;
	long get_attempts;
	long add_count;
	long get_count;
} queue_t;

queue_t* queue_init(int max_count);
void queue_destroy(queue_t *q);
int queue_add(queue_t *q, int val);
int queue_get(queue_t *q, int *val);
void queue_print_stats(queue_t *q);

#endif		// __FITOS_QUEUE_H__
