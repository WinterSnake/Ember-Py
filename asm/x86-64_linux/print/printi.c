/*
	Ember ASM: Debug Print Int

	Written By: Ryan Smith
*/
#ifdef BUFFER_CAPACITY
	#undef BUFFER_CAPACITY
#endif
#define BUFFER_CAPACITY 32

#include <unistd.h>

void PRINTI(long long int value)
{
	int bufferSize = 1;
	char buffer[BUFFER_CAPACITY];
	buffer[BUFFER_CAPACITY - 1] = '\n';
	int isNegative = value < 0;
	if (isNegative)
		value *= -1;
	unsigned long long int uValue = (unsigned long long int)value;
	// Write: value
	do
	{
		buffer[BUFFER_CAPACITY - 1 - (bufferSize++)] = uValue % 10 + '0';
		uValue /= 10;
	} while(uValue);
	// Write: sign
	if (isNegative)
		buffer[BUFFER_CAPACITY - 1 - (bufferSize++)] = '-';
	write(1, &buffer[BUFFER_CAPACITY - bufferSize], bufferSize);
}
