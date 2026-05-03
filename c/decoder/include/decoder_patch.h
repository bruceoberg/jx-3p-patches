/*
 * decoder_patch.h
 * JX3P patch format decoder
 * Convert bitstream into decoded JX3P patch/bank collection
 * 
 * See README.txt for license and installation notes.
 */


#include "jx3p_patch.h"


#define PATCH_RECORD_LENGTH		334	// full record length
#define PATCH_DATA_LENGTH		286 // data (non-padding)
#define PATCH_PADDING_LENGTH	48	// padding of 1s after record


// Decoder state
typedef struct {
	unsigned int bucket[PATCH_DATA_LENGTH];	// bit bucket (when full, do decode)
	unsigned int bucket_pos;		// current position in bucket
	unsigned short int one_count;	// if > 11x1, must be tone; state=DS_SEARCHING
	unsigned short int state;		// decoder state (searching, collecting, decoding)
} Decoder_State;


// Decoder-facing alias for the shared patch struct (kept for source compatibility).
typedef jx3p_patch_t jx3p_format;


// master storage for all patches by bank
typedef struct {
	jx3p_format data [2][16];
} Patch_Collection;


// function prototypes

Patch_Collection init_patch_collection();

Decoder_State init_decoder_state();

jx3p_format * get_patch(Patch_Collection * pc, int bank, int patch);
int set_patch(Patch_Collection * pc, int bank, int patch, jx3p_format * patchdata);

int decode_bitstream(int bits[], int bit_len, Decoder_State *ds, Patch_Collection *pc);
int convert_patch(Decoder_State *ds, jx3p_format *cp);

char * print_csv_header();
char * print_csv_patch(jx3p_format * p);

// text label translators

char * patch_identifier(int cd, int n);

char * dco_range(int n);

char * dco1_waveform(int n);

char * dco2_waveform(int n);

char * dco_crossmod(int n);

char * lfo_waveform(int n);

char * env_polarity(int n);

char * vca_mode(int n);
