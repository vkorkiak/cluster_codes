/*
 find_val.cc -- Faster parsing
 Copyright (C) 2012 Visa Korkiakoski <korkiakoski@strw.leidenuniv.nl>
 
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <stdio.h>
#include "string.h"
#include "oct.h"

#define NBUF 1024


// void
// mexFunction (int nlhs, mxArray *plhs[], int nrhs, 
//              const mxArray *prhs[])


/*!
 @brief Finds a value for given key

 @author Visa Korkiakoski
*/
DEFUN_DLD(find_val, args, nargout, 
	  "[val vals] = find_val(fname, keyname, nonum)")
{
  const double  *phsm;
  int            po1, po2;
  octave_value_list retval;

  int nargin = args.length();
  if (nargin != 2 && nargin != 3) {
    print_usage();
    return octave_value_list();
  }

  // printf("Here I am...\n");

  // Get filename
  if (! args(0).is_sq_string ()) {
    print_usage();
    return octave_value_list();
  }
  charMatrix ch1 = args(0).char_matrix_value ();
  std::string fnameStr = ch1.row_as_string(0);
  const char *fname = fnameStr.c_str();

  // printf("fname: %s...\n", fname);


  // Get keyname
  if (! args(1).is_sq_string ()) {
    print_usage();
    return octave_value_list();
  }
  charMatrix ch2 = args(1).char_matrix_value ();
  std::string keynameStr = ch2.row_as_string(0);
  const char *keyname = keynameStr.c_str();

  // printf("keyname: %s...\n", keyname);


  // Get nonum flag
  int nonum = 0;
  if (nargin == 3) {
    nonum = (int)(args(2).array_value())(0);
  }


  //
  // Go through input file
  //
  FILE *stream = fopen(fname, "rt");
  if (stream == NULL) {
    error("Could not open file %s", fname);
    return octave_value_list();
  }

  int  found=0;
  char str[NBUF];
  char valstr[NBUF];
  int i=0, stp, valst, nstr, nval;
  int nkey = strlen(keyname);
  while (! feof(stream)) {
    fgets(str, NBUF, stream);
    nstr = strlen(str);
    // Does it match with the key?
    stp=0;
    while (str[stp] == ' ' && stp<nstr)
      stp++; // remove ' '
    if (strncmp(str+stp, keyname, nkey) == 0) {

      // Find the value (string after '=')
      valst = stp;
      while (str[valst] != '=' && valst<nstr)
	valst++;
      valst++;
      while (str[valst] == ' ' && valst<nstr)
	valst++; // remove ' '

      // Get the value string
      memset(valstr, 0, NBUF);
      nval=0;
      while (str[valst + nval] != '%' && 
	     str[valst + nval] != '#' && 
	     str[valst + nval] != ';' && 
	     valst + nval<nstr) {
	// printf("-%c-<%d>-", str[valst + nval], str[valst + nval]);
	valstr[nval] = str[valst + nval];
	nval ++;
      }
      found=1;
      break;
    }// match with key

    // printf("%d> %s\n", i++, str);
  }
  fclose(stream);
 

  if (found) {
    double numval = atof(valstr);
    // printf("val (%s): %e\n", valstr, numval);


    NDArray theVal(1);
    theVal(0) = numval;
    return octave_value(theVal);

  } else {
    NDArray theVal;
    return octave_value(theVal);
  }

  return octave_value_list();
}
