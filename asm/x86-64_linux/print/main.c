#include "printf.c"
#include "printi.c"
#include "printu.c"

int main()
{
	// Ints
    PRINTI(0);  // 0 test
    PRINTI(-128);  // int8 MIN
    PRINTI(127);  // int8 MAX
    PRINTI(-32768);  // int16 MIN
    PRINTI(32767);  // int16 MAX
    PRINTI(-2147483648);  // int32 MIN
    PRINTI(2147483647);  // int32 MAX
    PRINTI(-9223372036854775807 - 1);  // int64 MIN
    PRINTI(9223372036854775807);  // int64 MAX
	// UInts
    PRINTU(0);  // 0 test
    PRINTU(255);  // uint8 MAX
    PRINTU(65535);  // uint16 MAX
    PRINTU(4294967295);  // uint32 MAX
    PRINTU(18446744073709551615U);  // uint64 MAX
	// Floats
	PRINTF(5.84);
	PRINTF(-13315.84846);
}
