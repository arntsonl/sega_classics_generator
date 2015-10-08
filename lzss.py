text_buf = None
lson = None
rson = None
dad = None
N = 4096

def InsertNode(r):
    global N
	global text_buf
	global lson
	global rson
	global dad

def lzss_compress(src, srclen, dstlen):
    global N
	global text_buf
	global lson
	global rson
	global dad

	F = 18
	THRESHOLD = 255
	init_chr = ' '
	
	textsize = 0
	codesize = 0
	text_buf = None
	match_position = 0
	match_length = 0
	lson = 0 
	dson = 0 
	dad = 0 
	
	EI = 12
	EJ = 4
	P = 2
	rless = P
	N = 1 << EI
	THRESHOLD = P
	F = (1 << EJ) + THRESHOLD

    NIL = N

	text_buf = [init_chr] * (N+F-1)
	lson = [NIL] * (N+1)
	rson = [NIL] * (N+257)
	dad = [NIL] * (N+1)
	
	code_buf = [0] * 18
	code_buf_ptr = 1
	mask = 1
	s = 0
	r = N - F
	
	for len in range(0, F):
		if len > srclen:
			break
		text_buf[r + len] = src[len]

	for i in range(1, F+1):
		InsertNode(r-i)
	InsertNode(r)

void InsertNode(int r)
	/* Inserts string of length F, text_buf[r..r+F-1], into one of the
	   trees (text_buf[r]'th tree) and returns the longest-match position
	   and length via the global variables match_position and match_length.
	   If match_length = F, then removes the old node in favor of the new
	   one, because the old one will be deleted sooner.
	   Note r plays double role, as tree node and position in buffer. */
{
	int  i, p, cmp;
	unsigned char  *key;

	cmp = 1;  key = &text_buf[r];  p = N + 1 + key[0];
	rson[r] = lson[r] = NIL;  match_length = 0;
	for ( ; ; ) {
		if (cmp >= 0) {
			if (rson[p] != NIL) p = rson[p];
			else {  rson[p] = r;  dad[r] = p;  return;  }
		} else {
			if (lson[p] != NIL) p = lson[p];
			else {  lson[p] = r;  dad[r] = p;  return;  }
		}
		for (i = 1; i < F; i++)
			if ((cmp = key[i] - text_buf[p + i]) != 0)  break;
		if (i > match_length) {
			match_position = p;
			if ((match_length = i) >= F)  break;
		}
	}
	dad[r] = dad[p];  lson[r] = lson[p];  rson[r] = rson[p];
	dad[lson[p]] = r;  dad[rson[p]] = r;
	if (rson[dad[p]] == p) rson[dad[p]] = r;
	else                   lson[dad[p]] = r;
	dad[p] = NIL;  /* remove p */
}

void DeleteNode(int p)  /* deletes node p from tree */
{
	int  q;
	
	if (dad[p] == NIL) return;  /* not in tree */
	if (rson[p] == NIL) q = lson[p];
	else if (lson[p] == NIL) q = rson[p];
	else {
		q = lson[p];
		if (rson[q] != NIL) {
			do {  q = rson[q];  } while (rson[q] != NIL);
			rson[dad[q]] = lson[q];  dad[lson[q]] = dad[q];
			lson[q] = lson[p];  dad[lson[p]] = q;
		}
		rson[q] = rson[p];  dad[rson[p]] = q;
	}
	dad[q] = dad[p];
	if (rson[dad[p]] == p) rson[dad[p]] = q;  else lson[dad[p]] = q;
	dad[p] = NIL;
}

void Encode(void)
{
	int  i, c, len, r, s, last_match_length, code_buf_ptr;
	unsigned char  code_buf[17], mask;
	
	InitTree();  /* initialize trees */
	code_buf[0] = 0;  /* code_buf[1..16] saves eight units of code, and
		code_buf[0] works as eight flags, "1" representing that the unit
		is an unencoded letter (1 byte), "0" a position-and-length pair
		(2 bytes).  Thus, eight units require at most 16 bytes of code. */
	code_buf_ptr = mask = 1;
	s = 0;  r = N - F;
	//for (i = s; i < r; i++) text_buf[i] = init_chr;  /* Clear the buffer with
	//	any character that will appear often. */
    lzss_set_window(text_buf, r, init_chr);

	for (len = 0; len < F && (c = lzss_xgetc(infile)) != EOF; len++)
		text_buf[r + len] = c;  /* Read F bytes into the last F bytes of
			the buffer */
	if ((textsize = len) == 0) return;  /* text of size zero */
	for (i = 1; i <= F; i++) InsertNode(r - i);  /* Insert the F strings,
		each of which begins with one or more 'space' characters.  Note
		the order in which these strings are inserted.  This way,
		degenerate trees will be less likely to occur. */
	InsertNode(r);  /* Finally, insert the whole string just read.  The
		global variables match_length and match_position are set. */
	do {
		if (match_length > len) match_length = len;  /* match_length
			may be spuriously long near the end of text. */
		if (match_length <= THRESHOLD) {
			match_length = 1;  /* Not long enough match.  Send one byte. */
			code_buf[0] |= mask;  /* 'send one byte' flag */
			code_buf[code_buf_ptr++] = text_buf[r];  /* Send uncoded. */
		} else {
			code_buf[code_buf_ptr++] = (unsigned char) match_position;
			code_buf[code_buf_ptr++] = (unsigned char)
				(((match_position >> 4) & 0xf0)
			  | (match_length - (THRESHOLD + 1)));  /* Send position and
					length pair. Note match_length > THRESHOLD. */
		}
		if ((mask <<= 1) == 0) {  /* Shift mask left one bit. */
			for (i = 0; i < code_buf_ptr; i++)  /* Send at most 8 units of */
				lzss_xputc(code_buf[i], outfile);     /* code together */
			codesize += code_buf_ptr;
			code_buf[0] = 0;  code_buf_ptr = mask = 1;
		}
		last_match_length = match_length;
		for (i = 0; i < last_match_length &&
				(c = lzss_xgetc(infile)) != EOF; i++) {
			DeleteNode(s);		/* Delete old strings and */
			text_buf[s] = c;	/* read new bytes */
			if (s < F - 1) text_buf[s + N] = c;  /* If the position is
				near the end of buffer, extend the buffer to make
				string comparison easier. */
			s = (s + 1) & (N - 1);  r = (r + 1) & (N - 1);
				/* Since this is a ring buffer, increment the position
				   modulo N. */
			InsertNode(r);	/* Register the string in text_buf[r..r+F-1] */
		}
		while (i++ < last_match_length) {	/* After the end of text, */
			DeleteNode(s);					/* no need to read, but */
			s = (s + 1) & (N - 1);  r = (r + 1) & (N - 1);
			if (--len) InsertNode(r);		/* buffer may not be empty. */
		}
	} while (len > 0);	/* until length of string to be processed is zero */
	if (code_buf_ptr > 1) {		/* Send remaining code. */
		for (i = 0; i < code_buf_ptr; i++) lzss_xputc(code_buf[i], outfile);
		codesize += code_buf_ptr;
	}
}

    infile   = in;
    infilel  = in + insz;
    outfile  = out;
    outfilel = out + outsz;

    if(parameters) {
        int     EI = 12, EJ = 4, P = 2, rless = P;

        get_parameter_numbers(parameters,
            &EI, &EJ, &P, &rless, &init_chr, NULL);

        if((EI < 0) || (EI >= 0xffff)) return -1;
        if((EJ < 0) || (EJ >= 31))     return -1;
        if((P  < 0) || (P  >= 0xffff)) return -1;

        if(EI >= 16) N = EI;
        else         N = 1 << EI;
        THRESHOLD = P;
        F = (1 << EJ) + THRESHOLD;
        // rless unused
    }

    NIL = N;
    text_buf = realloc(text_buf, N + F - 1);
    lson     = realloc(lson, sizeof(int) * (N + 1));
    rson     = realloc(rson, sizeof(int) * (N + 257));
    dad      = realloc(dad,  sizeof(int) * (N + 1));

    Encode();
    return(outfile - out);
}








	
def unlzss(src, srclen, dstlen):
	EI = 12
	EJ = 4
	P = 2
	N = 1 << EI
	F = 1 << EJ
	rless = P
	init_chr = ' '
	
	# create our buffer
	dst = []
	for i in xrange(0, dstlen):
		dst.append(0)
	
	# create our slide window
	slide_winsz = N
	slide_win = []*N
	for i in xrange(0, N):
		slide_win.append(init_chr)
	
	# setup our variables
	r = (N-F) - rless
	N = N - 1
	F = F - 1
	
	# substitute pointer variables
	src_idx = 0
	src_end = srclen
	dst_idx = 0
	dst_end = dstlen
	
	quit = False
	flags = 0
	while quit == False:
		if (flags & 0x100) == 0:
			if src_idx >= src_end:
				break			
			flags = ord(src[src_idx]) | 0xff00
			src_idx += 1
		if (flags & 1):
			if src_idx >= src_end:
				break
			c = src[src_idx]
			src_idx += 1
			if dst_idx >= dst_end:
				quit = True # error?
				break
			dst[dst_idx] = c
			dst_idx += 1
			slide_win[r] = c
			r = (r + 1) & N
		else:
			if src_idx >= src_end:
				break
			i = ord(src[src_idx])
			src_idx += 1
			if src_idx >= src_end:
				break
			j = ord(src[src_idx])
			src_idx += 1
			i = i | ((j >> EJ) << 8)
			j = (j & F) + P
			for k in xrange(0, j+1):
				c = slide_win[(i+k)&N]
				if dst_idx >= dst_end:
					quit = True
					break
				dst[dst_idx] = c
				dst_idx += 1
				slide_win[r] = c
				r = (r + 1) & N
		flags = flags >> 1
		
	return dst

		
