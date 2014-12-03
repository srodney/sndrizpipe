
c
c this is the current version:
c
c wfc3uv_ctereverse_wSUB.F.2014.09.12
c

 
#define _WDIM_ 999      /* maximum number of traps ; don't touch  */

c-----------------------------------------------------------------------
c-----------------------------------------------------------------------
c
c UPDATES:
c
c Nov  14, 2014:  set things up to operate on some full-amp QUAD filters
c Nov  14, 2014:  removed fcarry0 variation (to ensure repeatability)
c 
c Sept 12, 2014:  add subarrays c512a, c512b, c512d 
c                 (c512c was already there...)
c Sept 23, 2014:  modified to preserve the extra header
c                 info in the output flc file.
c 
c-----------------------------------------------------------------------
 
c
c this particular version has been reformulated to
c work on selected subarray images ; it will not output
c "rac" files for the subarrays, but it will output
c "flc" files for them, if the user supplies an "flt"
c image (along with the "raw" image, of course)
c
c
c subarray apertures for which this should work:
c
c NAP NAPu NAME               APERTURE=            EXAMPLE IMAGE
c --- ---- ----------------   ------------------   ------------------- 
c 01  (01) FULL FRAME
c 02  (02) UVIS1-2K4-SUB      'UVIS1-2K4-SUB   '   ibnc04n3q_raw.fits                                                              
c 03  (03) UVIS1-2K2A-SUB     'UVIS1-2K2A-SUB  '   ibqk07clq_raw.fits
c 04  (04) UVIS1-2K2B-SUB     'UVIS1-2K2B-SUB  '   ibsp10xvq_raw.fits
c 05  (05) UVIS2-2K2C-SUB     'UVIS2-2K2C-SUB  '   ibqt04pkq_raw.fits
c 06  (06) UVIS2-C1K1C-SUB    'UVIS2-C1K1C-SUB '   ibqt03m9q_raw.fits
c 07  (07) UVIS2-C512C-SUB    'UVIS2-C512C-SUB '   ibt401flq_raw.fits
c 08  (07) UVIS2-C512D-SUB    'UVIS2-C512D-SUB '   ibbszjb7q_raw.fits
c 09  (07) UVIS1-C512A-SUB    'UVIS1-C512A-SUB '   ibuc51auq_raw.fits
c 10  (07) UVIS1-C512B-SUB    'UVIS1-C512B-SUB '   ibbsz8qyq_raw.fits
c-----------------------------------------------------------
c UNSUPPPORTED  UVIS2-M1K1C-SUB (no reference pixels) 
c-----------------------------------------------------------

 
c-----------------------------------------------------------
c QUICK-START ADVICE
c-----------------------------------------------------------
c
c STEP1)  COMPILE THE PROGRAM IN SOME DIRECTORY
c
c         g77 wfc3uv_ctereverse.F -o wfc3uv_ctereverse.e <cr>
c
c             * you can also use gfortran instead of g77
c             * the capital F is important; it invokes the
c               pre-compiler (which it needs)
c
c         Then you can run the program.  This particular routine
c         insists that all the exposures be in the same directory.
c         The executable can be in a different directory, but the
c         images you're reading in and operating on *must* be in
c         your current directory.  The reason is that the routine
c         takes the first 8+q characters as the image root, then
c         assumes that the 3-character image type designation
c         follows an underscore (ie, _raw, _flt, etc).
c
c
c STEP2)  TEST THE COMPILATION; SEE PARAMETERS
c
c         You can run the program without any arguments to
c         get a list of its arguments:
c
c         ./wfc3uv_ctereverse.e <cr>
c
c         The full README has a discussion of the indivudual
c         arguments.  This quick-start README will only touch
c         on the "standard" operation.
c
c
c STEP3)  EXAMPLE OF BASIC OPERATION
c
c         The most basic way of running the routine would be
c         to correct an "_flt" image and generate an "_flc" image.
c         This is akin to what the ACS pipeline produces, but
c         the UVIS routine is unable to operate on the _flt alone,
c         since the _flt may have had some post-flash electrons
c         removed, and these electrons are important to help the
c         routine estimate how charge may have been redistributed
c         during readout.
c
c         ./wfc3uv_ctereverse.e ibxd90xeq_raw.fits FLC+ <cr>
c
c         Running it without the FLC+ option will generate the
c         correction, but the routine will stop after generating
c         the "rac" file (the corrected "raw").  The program
c         won't presume that there is an "flt" file to correct
c         and make an "flc" file.
c
c
c STEP4)  EXAMINE THE IMAGES
c
c         Blink between the "flt" and the "flc" images; if you
c         output various intermediate images, look at what has
c         changed.
c
c
c STEP5)  CONTINUE PROCESSING AS USUAL
c
c         If you made the "flc" images, then just analyze them
c         or astro-drizzle them as you would "flt" files.
c--------------------------------------------------------------
 
 
 
 
 
c--------------------------------------------------------------
c LIST OF AVAILABLE PARAMETERS
c-----------------------------------------------------------
c
c Running the routine witn no arguments will give a list of
c parameters:
c
c  ./wfc3uv_ctereverse.e <cr>
c
c  This program requires 1+ argument, but can take several
c  optional parameters:
c
c  ./wfc3uv_ctereverse.e ibxd90xaq_raw.fits ...
c                        [V+] [I-] [RN=3.25] [CR-]
c                        [RAC-] [FLC+] [INFO]
c
c  The arguments can be in any order
c
c    *raw.fits : list of full-frame raw.fits images
c                (no directories allowed: "_raw" must
c                 be in characters 10:13)
c
c    INFO      : outputs the fully populated model
c                parameters, then stops
c
c    RN=real*4 : give an amount of RN mitigation to      (default 3.25)
c                allow for
c
c    V+/V-     : verbose on/off                          (default OFF)
c
c    I+/I-     : outut all intermed files on/off         (default OFF)
c                The intermediate files *all* are
c                formatted in "RAZ" format; it's an
c                abutted format with amps CDAB left
c                to right, with 2103x2070 for each,
c                with readout down and to the left.
c                Preserves horizontal pre-/post-scan
c                and vertical overscan. Total size is
c                8412x2070.
c
c    CR+/CR-   : prevent oversub readout  CRs on/off     (default ON)
c
c    RAC+/RAC- : output the _rac.fits file               (default ON)
c
c
c    FLC+/FLC- : output the _flc.fits file               (default OFF)
c                (using the raw, flt, and generated rac)
c
c There are some non-standard parameters for outputting
c things in formats the author finds convenient, but they
c will not be described here.
c
c--------------------------------------------------------------
 
 
 
 
 
c--------------------------------------------------------------
c CAVEATS
c--------------------------------------------------------------
c
c The current model is not perfect.  Here are a few caveats.
c As users point out problems, I may add to this list here (and
c elsewhere) as I make improved releases.
c
c * When the background is low, readnoise mitigation is extremely
c   important; I have found that 3.25 is a reasonable amount of
c   noise to try to take out.  Of course, it's impossible to
c   know what is noise and what is signal, so it errs on the
c   conservative side by assuming as much as possible to be noise.
c   The alternative would be to make a hideously noisy image.
c   Just try operating on an image with no background and RN=0.0
c
c * I have found that the current model predicts *too* much flux
c   loss when the source flux is low and the background is low.
c   It does a good job predicting loss-mitigatoin as background
c   is increased, but predicts too much on low backgrounds.  This
c   is seen in Figure 1 of the brief write-up I am submitting along
c   with this code.
c
c   Clearly some assumptions the model is making are not completely
c   valid.  One possibility is that traps may not be randomly
c   distributed throughout the detector, but may be clumped.  This
c   would mean that packets might not interact with traps one at a
c   time, and perhaps there would be less high-trap losses as a result.
c   A second possilibity is that traps may not grab every electron
c   they can.  Perhaps a trap that grabs the 10th electron grabs
c   it only 25% of the time if there are exactly 10 electrons,
c   50% of the time if there are 12 electrons and 100% of the time
c   if there are 15 or more electrons.  This also would describe
c   the phenomenology of what I'm seeing.
c
c   I will be investigating ways to make the model better describe
c   the observations.  Once done, it will do a better job with
c   the faint sources on low background, but one should recall that
c   readnoise limits what we can do in this regime, even with
c   a model that perfectly describes CTE losses.
c
c * I have not implemented any column-by-column corrections.
c   Wait for the next release.  The plan is to use both the
c   parallel overscans *and* the charge-injection monitor program
c   to better poinpoint where the traps are within the detector,
c   both column-wise and row-within-column-wise.
c
c * I have not yet changed the error arrays to reflect the
c   uncertainty involved in the charge-redistribution process.
c
c-------------------------------------------------------------
 
 
 
c-------------------------------------------------------------
c
c This FORTRAN program will perform all the necessary steps to
c go from a wfc3uvis "_raw.fits" file to distortion-corrected
c wfc3uvis "_rac.fits" file.
c
c
      program wfc3uv_ctereverse
      implicit none
 
c
c----------------------------------------------------
c
      character*80 RAW_HEADER(360) ! contains the header information
 
      character*80 FILE_RAW  ! original raw file
      character*80 FILE_RAZ  ! blev-cor raz image
      character*80 FILE_RNZ  ! noisy component
      character*80 FILE_RSZ  ! smoothest component
      character*80 FILE_RSC  ! corrected smoothest component
      character*80 FILE_FFF  ! CTE scaling for each pixel
      character*80 FILE_CHZ  ! change in pixel distribution
      character*80 FILE_RZC  ! corrected raz image
      character*80 FILE_RAC  ! corrected raw image
 
      character*80 FILE_FLT  ! uncorrected flt
      character*80 FILE_FLC  !   corrected flt
      character*80 FILE_WJ2  ! Jay's private integer*2 format (flt)
      character*80 FILE_WJC  ! Jay's private integer*2 format (flc)
 
      real pixz_raw(8412,2070) ! this is the raw image in abutted 4-amp format; includes bias offset (in DNs)
      real pixz_raz(8412,2070) ! this is the rudimentary blev-cor version of the raw image (in electrons)
      real pixz_rsz(8412,2070) ! this is the un-noisy ("smooth") version of the raz file
      real pixz_rnz(8412,2070) ! this is the pure-noise version of the raz file (raz = rsz+rnz)
      real pixz_rsc(8412,2070) ! this is the corrected version of the un-noisy raz file
      real pixz_fff(8412,2070) ! this reports the CTE scaling for each pixel; prop to the # of traps experienced
      real pixz_chz(8412,2070) ! this reports the redistribution of charge
      real pixz_rzc(8412,2070) ! this is the corrected version of the raz image (in electrons)
      real pixz_rac(8412,2070) ! this the corrected version of the raw image (back in DNs)
      real pixz_flt(8412,2070)
      real pixz_flc(8412,2070)
 
      real pixr_wj2(4096,4096)
      real pixr_wjc(4096,4096)
 
      integer NARG, NARGs
      logical isparam(999)
 
      real CTE_FF
      real find_FF
      character*12 DATE_STRING
      real rDATu, rDAT0, rDAT1
c
c----------------------------------------------------
c
      integer        q_w(_WDIM_)     ! output: the run of charge with level #L
      real        dpde_w(_WDIM_)     ! output: the run of charge loss with level #L
      integer    tprof_w(_WDIM_)     ! output: the length of trail for charge level #L
      real      rprof_wt(_WDIM_,100) ! output: the emission probability as fn of downhill pixel
      real      cprof_wt(_WDIM_,100) ! output: the cumulative probability cprof_t( 0001 ) = 1.000-rprof_t(1)
      integer   Ws
      character*80 CTE_HEADER(72)
      integer      H, Hs
c
c----------------------------------------------------
c
      logical DO_CRPROTECT
      data DO_CRPROTECT/.true./
 
      real    RNMIT
      data    RNMIT/3.25/
 
      logical DO_INTERMED
      data    DO_INTERMED/.false./
 
      logical VERBOSE
      common /VERBOSE_/VERBOSE
      data    VERBOSE/.false./
 
      logical OUTPUT_RAC
      data    OUTPUT_RAC/.true./
 
      logical OUTPUT_FLC
      data    OUTPUT_FLC/.false./
 
      logical OUTPUT_WJC
      data    OUTPUT_WJC/.false./
 
      logical OUTPUT_RZC
      data    OUTPUT_RZC/.false./
 
      logical OUTPUT_FLT2WJC
      data    OUTPUT_FLT2WJC/.false./
 
      integer START
      data    START/0/
 
      integer TRATS
      data    TRATS/9/
c
c----------------------------------------------------
c
      character*80 STRING
c
c----------------------------------------------------
c
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
      data    LINUX_FLAG/.true./
      integer*4 itest
      byte    b(4)
      equivalence (itest,b)
      logical LINUX_TEST
      integer i,j
 
      itest = 1
 
      LINUX_TEST = .false.
      if (b(4).eq.1.and.b(1).eq.0) LINUX_TEST = .true.
      if (b(1).eq.1.and.b(4).eq.0) LINUX_TEST = .true.
      if (.not.LINUX_TEST) stop 'CANNOT SET INTEL FLAG'
 
      LINUX_FLAG = .true.
      if (b(4).eq.1.and.b(1).eq.0) LINUX_FLAG = .false. ! solaris
 
      NARGs = iargc()
 
 
c--------------------------------------------------------------------
c
c IF ON ARGUMENTS GIVEN, THEN TELL THE USER HOW TO USE IT
c
      if (NARGs.lt.1) then
         print*,'                                                    '
         print*,'This program requires 1+ argument, but can take     '
         print*,'several optional parameters:                        '
         print*,'                                                    '
         print*,'./wfc3uv_ctereverse.e ibxd90xaq_raw.fits ...        '
         print*,'                      [V+] [I-] [RN=3.25] [CR-]     '
         print*,'                      [RAC-] [FLC+] [INFO]          '
         print*,'                                                    '
         print*,'The arguments can be in any order                   '
         print*,'                                                    '
         print*,'    *raw.fits : list of one or more full-frame      '
         print*,'                raw.fits images                     '
         print*,'                (no directories allowed:            '
         print*,'                 "_raw" must be in characters 10:13)'
         print*,'    INFO      : outputs the fully populated model   '
         print*,'                parameters then stops               '
         print*,'    RN=real*4 : give an amount of RN mitigation to  '
         print*,'                allow for (default 3.25 e-)         '
         print*,'    V+/V-     : verbose on/off (default OFF)        '
         print*,'    CR+/CR-   : prevent oversubtraction of readout  '
         print*,'                CRs on/off (default ON)             '
         print*,'    RAC+/RAC- : output the _rac.fits file           '
         print*,'                (default ON)                        '
         print*,'    FLC+/FLC- : output the _flc.fits file (using the'
         print*,'                raw, flt, and generated rac         '
         print*,'                (default OFF)                       '
         print*,'    I+/I-     : intermed files on/off (default OFF) '
         print*,'                KEY TO INTERMED FILES:              '
         print*,'                _raz: original blev-cor raw z-format'
         print*,'                _rnz: noise-only version of raz     '
         print*,'                _rsz: non-noise version of raz      '
         print*,'                _fff: tot trap scale for each pixel '
         print*,'                _rsc: cte-corrected _rsz image      '
         print*,'                _rzc: cte-corrected _raz image      '
         print*,'                      (_rzc = _rsc + _rnz)          '
         print*,'                                                    '
         print*,'                                                    '
         print*,'The output for the routine is best viewed with at   '
         print*,'least 225 columns ; you could run it and pipe it to '
         print*,'"cut -c1-80", but that would throw away a lot of    '
         print*,'good diagnostic information.                        '
         print*,'                                                    '
         print*,'                                                    '
         stop
         endif
 
 
 
c--------------------------------------------------------------------
c
c SEARCH THE COMMAND LINE FOR FLAGS, AND SET THEM
c
      do NARG = 1, NARGs
         if (NARG.gt.999) stop 'max number of args = 999'
         isparam(NARG) = .false. ! flag whether each argument is an image to run on
         call getarg(NARG,STRING)
         if (STRING(1:4).eq.'INFO') then
           call setup_cte_w(q_w,dpde_w,tprof_w,rprof_wt,cprof_wt,Ws,
     .                      .true.)
           stop
           endif
         if (STRING(1:2).eq.'I+'  ) then
            DO_INTERMED  = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:2).eq.'I-'  ) then
            DO_INTERMED  = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:2).eq.'V+'  ) then
            VERBOSE      = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:2).eq.'V-'  ) then
            VERBOSE      = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:3).eq.'CR+' ) then
            DO_CRPROTECT = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:3).eq.'CR-' ) then
            DO_CRPROTECT = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:3).eq.'RN=' ) then
            read(STRING(4:10),*) RNMIT
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'RAC+') then
            OUTPUT_RAC = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'RAC-') then
            OUTPUT_RAC = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'FLC+') then
            OUTPUT_FLC = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'FLC-') then
            OUTPUT_FLC = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'WJC+') then
            OUTPUT_WJC = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'WJC-') then
            OUTPUT_WJC = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'RZC+') then
            OUTPUT_RZC = .true.
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'RZC-') then
            OUTPUT_RZC = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:8).eq.'FLT2WJC-') then
            OUTPUT_FLT2WJC = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:8).eq.'FLT2WJC+') then
            OUTPUT_FLT2WJC = .true.
            OUTPUT_RAC     = .false.
            isparam(NARG) = .true.
            endif
         if (STRING(1:6).eq.'START=') then
            read(STRING(7:7),*) START
            isparam(NARG) = .true.
            endif
         if (STRING(1:4).eq.'END=') then
            read(STRING(5:5),*) TRATS
            isparam(NARG) = .true.
            endif
         if (STRING(1:6).eq.'TRATS=') then
            read(STRING(7:7),*) TRATS
            isparam(NARG) = .true.
            endif
         if (.not.isparam(NARG).and.
     .       STRING(11:13).ne.'raw') then
             print*,'INVALID ARGUMENT: ',STRING(1:20)
             stop
             endif
         enddo
 
 
c-------------------------------------------------------------------------
c
c OUTPUT THE PARAMETERS THAT WE WILL USE FOR THIS RUN
c
      print*,'            '
      print*,'   wfc3uv_ctereverse.e  '
      print*,'            parameters: '
      print*,'            '
      print*,'        INTEL_BYTEORDR: ',LINUX_FLAG
      print*,'        RNMIT         : ',RNMIT
      print*,'        DO_INTERMED   : ',DO_INTERMED
      print*,'        DO_CRPROTECT  : ',DO_CRPROTECT
      print*,'        VERBOSE       : ',VERBOSE
      print*,'        OUTPUT_RZC    : ',OUTPUT_RZC
      print*,'        OUTPUT_RAC    : ',OUTPUT_RAC
      print*,'        OUTPUT_FLC    : ',OUTPUT_FLC
      print*,'        OUTPUT_FLT2WJC: ',OUTPUT_FLT2WJC
      print*,'        VERBOSE       : ',VERBOSE
      print*,'                 '
 
 
 
c-------------------------------------------------------------------------
c
c TAKE THE PARAMETRIZED CTE MODEL IN THE BLOCK DATA STATMENTS AND POPULATE
c THE DETAILED MODEL
c
      print*,'                                                        '
      print*,'********************************************************'
      print*,'*****                                                   '
      print*,'***** CTE MODEL STEP0:   POPULATE THE DETAILED CTE MODEL'
      print*,'*****                    FROM THE SIMPLIFIED PARAMETERS '
      print*,'*****                                                   '
      print*,'                                                        '
 
      call setup_cte_w(q_w,dpde_w,tprof_w,rprof_wt,cprof_wt,Ws,.false.)
 
 
 
c-------------------------------------------------------------------------
c
c GO THROUGH THE ARGUMENTS AND IDENTIFY THE _RAW IMAGES TO OPERATE ON
c
      do NARG = 1, NARGs
 
         call getarg(NARG,STRING)
 
         if (isparam(NARG)) goto 999 ! if this arg was a parameter, skip
 
         FILE_RAW = STRING
 
         FILE_RAZ = FILE_RAW
         FILE_RNZ = FILE_RAW
         FILE_RSZ = FILE_RAW
         FILE_RSC = FILE_RAW
         FILE_FFF = FILE_RAW
         FILE_CHZ = FILE_RAW
         FILE_RZC = FILE_RAW
         FILE_RAC = FILE_RAW
         FILE_FLT = FILE_RAW
         FILE_FLC = FILE_RAW
         FILE_WJ2 = FILE_RAW
         FILE_WJC = FILE_RAW
 
         FILE_RAZ(11:13) = 'raz'
         FILE_RNZ(11:13) = 'rnz'
         FILE_RSZ(11:13) = 'rsz'
         FILE_RSC(11:13) = 'rsc'
         FILE_FFF(11:13) = 'fff'
         FILE_RZC(11:13) = 'rzc'
         FILE_RAC(11:13) = 'rac'
         FILE_CHZ(11:13) = 'chz'
         FILE_FLT(11:13) = 'flt'
         FILE_FLC(11:13) = 'flc'
         FILE_WJ2(11:13) = 'WJ2'
         FILE_WJC(11:13) = 'WJC'
 
         if (FILE_RAW(10:13).eq.'_raz') then ! if you input a raz file, it'll skip blevcor
            DO_INTERMED = .true.       ! make sure to output intermed files
            TRATS = 5                  ! stop after generation of rzc...
            goto 2
            endif
 
         if (FILE_RAW(10:13).ne.'_raw') then
            print*,'                             '
            print*,'   wfc3uv_raw2rac.e ERROR    '
            print*,'                             '
            print*,'       ARGUMENT # ',NARG,' : ',FILE_RAW(1:20)
            print*,'                                 '
            print*,'          IS NEITHER A PARAMETER '
            print*,'          NOR A _raw.fits FILE   '
            print*,'                                 '
            stop
            endif
 
         print*,'                                                      '
         print*,'******************************************************'
         print*,'*****                                                 '
         print*,'***** NEXT wfc3uv_raw2rac ARG#: ',
     .                 NARG,'  FILE = ',FILE_RAW(1:20)
         print*,'*****                                                 '
         print*,'                                                      '
 
 
         if (OUTPUT_FLC.or.OUTPUT_FLT2WJC) then
            open(10,file=FILE_FLT,status='old',err=666)
            close(10)
            endif
 
         if (OUTPUT_WJC) then
            open(10,file=FILE_WJ2,status='old',err=668)
            close(10)
            endif
 
c-----------------------------------------------
c
c STEP1: READ IN THE RAW IMAGE...
c
    1    continue
         print*,' '
         print*,'******************************************************'
         print*,'***** '
         print*,'***** CTE MODEL STEP1:   READ IN RAW IMAGE'
         print*,'***** '
         print*,' '
 
         call fitshead2string(FILE_RAW,RAW_HEADER)
         call sub_wfc3uv_read_raw(FILE_RAW,pixz_raw)

         CTE_FF = find_FF(RAW_HEADER,DATE_STRING,rDATu,rDAT0,rDAT1)
         print*,'                  '
         print*,'     DATE_STRING: ',DATE_STRING
         print*,'           rDATu: ',rDATu
         print*,'           rDAT0: ',rDAT0
         print*,'           rDAT1: ',rDAT1
         print*,'          CTE_FF: ',CTE_FF
         print*,'                  '
 
c
c        construct two pages of a header info to describe the model
c
         call fill_hdr_page(CTE_HEADER,Hs,
     .                      q_w,dpde_w,tprof_w,rprof_wt,cprof_wt,Ws,
     .                      CTE_FF,DATE_STRING,rDATu,rDAT0,rDAT1,
     .                      FILE_RAW, FILE_RAC,
     .                      DO_CRPROTECT, RNMIT)
 
         if (.false.) then
            print*,'                  '
            print*,'HEADER TO ADD...  '
            print*,'                  '
            open(13,file='LOGA.HEADER',status='unknown')
            do H = 1, Hs
               write( *,'(''HEADER LINE: H'',i2.2,2x,80a)')
     .                                   H,CTE_HEADER(H)(1:80)
               write(13,'(''HEADER LINE: H'',i2.2,2x,80a)')
     .                                   H,CTE_HEADER(H)(1:80)
               enddo
            close(13)
            print*,'                  '
            print*,'                  '
            endif
 
c-----------------------------------------------
c
c STEP2: DO THE BLEV CORRECTION
c
 
    2    continue
         if (START.gt.2) then
            print*,'***** WARM START READ STEP2 OUTPUT: ',FILE_RAZ(1:20)
            call readfits_r4(FILE_RAZ,pixz_raz,8412,2070)
            goto 3
            endif
         print*,' '
         print*,'******************************************************'
         print*,'*****                                                 '
         print*,'***** CTE MODEL STEP2:   DO BLEV CORR                 '
         print*,'*****                    (RAW ---> RAZ)               '
         print*,'*****                                                 '
         print*,'                                                      '
         call sub_wfc3uv_raw2raz(pixz_raw,pixz_raz)
         if (DO_INTERMED) then
            print*,'    OUTPUT INTERMED FILE: ',FILE_RAZ(1:20)
            call writfits_r4h(FILE_RAZ,pixz_raz,8412,2070,RAW_HEADER)
            endif
         if (TRATS.eq.2) goto 999
 
 
 
c-----------------------------------------------
c
c STEP3: DO SMOOTH/NOISE SEPARATION
c
    3    continue
         if (START.gt.3) then
            print*,'***** WARM START READ STEP3 OUTPUT: ',FILE_RNZ(1:20)
            call readfits_r4(FILE_RNZ,pixz_rnz,8412,2070)
            print*,'                                  : ',FILE_RSZ(1:20)
            call readfits_r4(FILE_RSZ,pixz_rsz,8412,2070)
            goto 4
            endif
         print*,' '
         print*,'******************************************************'
         print*,'*****                                                 '
         print*,'***** CTE MODEL STEP3:   DETERMINE THE SMOOTHEST      '
         print*,'*****                    POSSIBLE SOURCE IMAGE        '
         print*,'*****                    (RAZ ---> RNZ+RSZ)           '
         print*,'*****                                                 '
         print*,'                                                      '
         call sub_wfc3uv_raz2rsz(pixz_raz,pixz_rsz,pixz_rnz,RNMIT)
         if (DO_INTERMED) then
            print*,'    OUTPUT INTERMED FILE: ',FILE_RNZ(1:20)
            call writfits_r4(FILE_RNZ,pixz_rnz,8412,2070)
            print*,'    OUTPUT INTERMED FILE: ',FILE_RSZ(1:20)
            call writfits_r4(FILE_RSZ,pixz_rsz,8412,2070)
            endif
         if (TRATS.eq.3) goto 999
 
 
 
c-----------------------------------------------
c
c STEP4: DEBLUR THE CTE TRAILS
c
    4    continue
         if (START.gt.4) then
            print*,'***** WARM START READ STEP4 OUTPUT: ',FILE_RSC(1:20)
            call readfits_r4(FILE_RSC,pixz_rsc,8412,2070)
            goto 5
            endif
         print*,' '
         print*,'******************************************************'
         print*,'*****                                                 '
         print*,'***** CTE MODEL STEP4:   DO THE REVERSE CTE CORRECTION'
         print*,'*****                    (RSZ ---> RSC)               '
         print*,'*****                                                 '
         print*,'                                                      '
         call sub_wfc3uv_raz2rac(pixz_rsz,pixz_rsc,pixz_fff,
     .                           CTE_FF,DO_CRPROTECT,
     .                           q_w,dpde_w,tprof_w,
     .                           rprof_wt,cprof_wt,Ws)
         if (DO_INTERMED) then
            print*,'    OUTPUT INTERMED FILE: ',FILE_RSC(1:20)
            call writfits_r4(FILE_RSC,pixz_rsc,8412,2070)
            print*,'    OUTPUT INTERMED FILE: ',FILE_FFF(1:20)
            call writfits_r4(FILE_FFF,pixz_fff,8412,2070)
            endif
         if (TRATS.eq.4) goto 999
 
 
 
c-----------------------------------------------
c
c STEP5: CONSTRUCTED THE FINAL CORRECTED IMAGE
c
    5    continue
         if (START.gt.5) then
            print*,'***** WARM START READ STEP5 OUTPUT: ',FILE_RZC(1:20)
            call readfits_r4(FILE_RZC,pixz_rzc,8412,2070)
            goto 6
            endif
         print*,' '
         print*,'******************************************************'
         print*,'*****                                                 '
         print*,'***** CTE MODEL STEP5:   ADOPT CORRECTION TO ORIGINAL '
         print*,'*****                    (RSC+RNZ --> RZC)            '
         print*,'*****                                                 '
         print*,'                                                      '
         call imgadd_r4(pixz_rsc,1.0000,pixz_rnz,pixz_rzc,8412,2070)
         if (DO_INTERMED.or.OUTPUT_RZC) then
            print*,'         OUTPUT INTERMED FILE: ',FILE_RZC(1:20)
            call writfits_r4(FILE_RZC,pixz_rzc,8412,2070)
            endif
         if (TRATS.eq.5) goto 999
 
 
 
c-----------------------------------------------
c
c STEP6: OUTPUT THE NEW RAC IMAGE
c
    6    continue
         if (START.gt.6) then
            print*,'***** WARM START READ STEP6 OUTPUT: ',FILE_CHZ(1:20)
            call readfits_r4(FILE_CHZ,pixz_chz,8412,2070)
            goto 7
            endif
         print*,' '
         print*,' '
         print*,'******************************************************'
         print*,'***** '
         print*,'***** CTE MODEL STEP6:   ADOPT CORRECTION TO ORIGINAL '
         print*,'*****                    (RZC ---> RAC   )            '
         print*,'***** '
         print*,'       (note, if you want to run CALWFC3 with this as '
         print*,'        the raw image, you will need to rename it to  '
         print*,'        _raw first.  The next version of CALWFC3      '
         print*,'        should allow _rac as a valid raw file.  Note  '
         print*,'        the _rac is a real*4 image and CALWFC3 is ok  '
         print*,'        with that)                                    '
         print*,'                                                      '
         call imgsub_r4(pixz_rzc,1.0000,pixz_raz,pixz_chz,8412,2070) ! compute change (in e-)
         call imgadd_r4(pixz_raw,0.6666,pixz_chz,pixz_rac,8412,2070) ! 0.666 scaling to turn chz to DNs
 
         if (OUTPUT_RAC) then
            call cowritfits_raw(FILE_RAW,FILE_RAC,pixz_rac,CTE_HEADER)
            endif
         if (DO_INTERMED) then
            call writfits_r4(FILE_CHZ,pixz_chz,8412,2070)
            endif
         if (TRATS.eq.6) goto 999
 
 
 
c-----------------------------------------------
c
c STEP7: OUTPUT THE NEW FLC IMAGE (IF DESIRED)
c
    7    continue
         if (OUTPUT_FLC.or.OUTPUT_FLT2WJC) then
            print*,' '
            print*,' '
            print*,'***************************************************'
            print*,'***** '
            print*,'***** CTE MODEL STEP7:   ADOPT CORRECTION TO ORIG  '
            print*,'*****                    (FLT ---> FLC   )         '
            print*,'***** '
            print*,' '
            print*,'     readfits_flt2pixz: ',FILE_FLT(1:20)
c           call readfits_flt2pixz(FILE_FLT,pixz_flt)
            call sub_wfc3uv_read_flt(FILE_FLT,pixz_flt)
            print*,'     imagadd_r4       : '
            call imgadd_r4(pixz_flt,1.000,pixz_chz,pixz_flc,8412,2070) ! 1.00 scaling to turn chz to e
            print*,'     cowritfits_flt   : ',FILE_FLT(1:20)
            print*,'                      : ',FILE_FLC(1:20)
            if (OUTPUT_FLC) then
                print*,'     cowritfit_flt... ',FILE_FLT(1:20)
                call cowritfits_flt(FILE_FLT,FILE_FLC,pixz_flc,
     .                              CTE_HEADER)
                endif
            if (OUTPUT_FLT2WJC) then
                print*,'     convert z2r... wj2'
                call convert_z2r(pixz_flt,pixr_wj2)
                print*,'     writfits_r2j... ',FILE_WJ2(1:20)
                call writfits_r2j(FILE_WJ2,pixr_wj2,4096,4096)
                print*,'     convert z2r... wjc'
                call convert_z2r(pixz_flc,pixr_wjc)
                print*,'     writfits_r2j... ',FILE_WJC(1:20)
                call writfits_r2j(FILE_WJC,pixr_wjc,4096,4096)
                endif
            endif
         if (TRATS.eq.7) goto 999
 
 
c-----------------------------------------------
c
c STEP8: OUTPUT THE NEW FLC IMAGE (IF DESIRED)
c
    8    continue
         if (OUTPUT_WJC) then
            print*,' '
            print*,' '
            print*,'***************************************************'
            print*,'***** '
            print*,'***** CTE MODEL STEP8:   ADOPT CORRECTION TO ORIG  '
            print*,'*****                    (WJ2 ---> WJC   )         '
            print*,'***** '
            print*,' '
            call readfits_j2r(FILE_WJ2,pixr_wj2,4096,4096)
            call convert_r2z(pixr_wj2,pixz_flt)
            call imgadd_r4(pixz_flt,1.000,pixz_chz,pixz_flc,8412,2070) ! 1.00 scaling to turn chz to e
            call convert_z2r(pixz_flc,pixr_wjc)
            call writfits_r2j(FILE_WJC,pixr_wjc,4096,4096)
            stop
            endif
         if (TRATS.eq.8) goto 999
 
 
  999    continue! if this argument was not a "_raw.fits" image to operate on...
         if (.false.) then
            print*,'                  '
            print*,'HEADER TO ADD...  '
            print*,'                  '
            open(13,file='LOGB.HEADER',status='unknown')
            do H = 1, Hs
               write( *,'(''HEADER LINE: H'',i2.2,2x,80a)') H,CTE_HEADER(H)
               write(13,'(''HEADER LINE: H'',i2.2,2x,80a)') H,CTE_HEADER(H)
               enddo
            close(13)
            print*,'                  '
            print*,'                  '
            endif
         enddo! NARG
 
      stop
 
 
 
  666 continue
      print*,'                                                   '
      print*,'ERROR EXIT:                                        '
      print*,'                                                   '
      print*,'   YOU WANT TO RUN THIS TO GENERATE AN FLC IMAGE,  '
      print*,'   BUT THERE IS NO CORRESPONDING _flt IMAGE IN THE '
      print*,'   CURRENT DIRECTORY.                              '
      print*,'                                                   '
      print*,'   FILE_FLT: ',FILE_FLT(1:20)
      print*,'                                                   '
      stop
 
  668 continue
      print*,'                                                   '
      print*,'ERROR EXIT:                                        '
      print*,'                                                   '
      print*,'   YOU WANT TO RUN THIS TO GENERATE AN WJC IMAGE,  '
      print*,'   BUT THERE IS NO CORRESPONDING _WJ2 IMAGE IN THE '
      print*,'   CURRENT DIRECTORY.                              '
      print*,'                                                   '
      print*,'   FILE_WJC: ',FILE_WJC(1:20)
      print*,'                                                   '
      stop
 
  667 continue
      print*,'            '
      print*,'ERROR EXIT: '
      print*,'            '
      print*,'   THE SPECIFIED _raw IMAGE CANNOT BE FOUND IN THE '
      print*,'   CURRENT DIRECTORY. '
      print*,'            '
      print*,'   FILE_RAW: ',FILE_RAW(1:20)
      print*,'            '
      stop
 
      end
 
 
 
 
 
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/setup_cte_w.f"
c****                                         
c*********************************************
                                              
 
#define _UDIM_     17  /* the number of points we specify run of cum.trap-vs-charge       */
#define _TDIM_     60  /* the maximum length of the trail we will concern ourselves with  */
#define _NITCTE_   07  /* the number iterations we do to get the charge down the detector */
#define _NITERN_   05  /* the number of iterations we use to reconstruct an image         */
 
 
c---------------------------------
c
c the packet size -vs- cumulative number of traps
c
      block data block_data_q1c2_u
      integer q1c2_u(2,_UDIM_)
      common /q1c2_u_ /q1c2_u           ! cumulative traps
      data    q1c2_u/
     .    00,   00,    ! 01
     .    01,   19,    ! 02
     .    02,   38,    ! 03
     .    03,   43,    ! 04
     .    07,   56,    ! 06
     .    12,   62,    ! 07
     .    20,   65,    ! 08
     .    30,   67,    ! 09
     .    50,   79,    ! 10
     .    70,   85,    ! 11
     .   100,   92,    ! 12
     .   316,  133,    ! 13
     .  1000,  183,    ! 14
     .  3160,  263,    ! 15
     . 10000,  393,    ! 16
     . 31600,  513,    ! 17
     . 99999,  533/    ! 18
      end
 
 
c--------------------------------------------
c
c this gives the charge release as a function
c of the number of shifts; this is parametrized
c to give the value at a limited number of
c points, t(16)
c
      block data block_data_chg_leak
      real    chg_leak(5,16)
      common /chg_leak_/chg_leak
c
c                     q=01    q=010   q=0100  q=01000 q=10000!   t  nt
c
      data chg_leak / 0.2000, 0.2000, 0.2000, 0.2000, 0.2000,!  01 (01) 01-01  1
     .                0.0850, 0.0850, 0.0850, 0.0850, 0.0850,!  02 (02) 02-02  1
     .                0.0675, 0.0675, 0.0675, 0.0675, 0.0675,!  03 (03) 03-03  1
     .                0.0410, 0.0410, 0.0410, 0.0410, 0.0410,!  05 (04) 04-06  3
     .                0.0260, 0.0260, 0.0260, 0.0260, 0.0260,!  08 (05) 07-09  3
     .                0.0160, 0.0160, 0.0160, 0.0160, 0.0160,!  12 (06) 10-13  4
     .                0.0130, 0.0130, 0.0130, 0.0130, 0.0130,!  16 (07) 14-17  4
     .                0.0100, 0.0100, 0.0100, 0.0100, 0.0100,!  20 (08) 18-22  5
     .                0.0060, 0.0060, 0.0060, 0.0060, 0.0060,!  25 (09) 23-27  5
     .                0.0030, 0.0030, 0.0030, 0.0030, 0.0030,!  30 (10) 28-34  7
     .                0.0020, 0.0020, 0.0020, 0.0020, 0.0020,!  40 (11) 35-44 10
     .                0.0010, 0.0010, 0.0010, 0.0010, 0.0010,!  50 (12) 45-54 10
     .                0.0000, 0.0000, 0.0000, 0.0000, 0.0000,!  60 (13) 55-64 10
     .                0.0000, 0.0000, 0.0000, 0.0000, 0.0000,!  70 (14) 65-74 10
     .                0.0000, 0.0000, 0.0000, 0.0000, 0.0000,!  80 (15) 75-84 10
     .                0.0000, 0.0000, 0.0000, 0.0000, 0.0000/!  90 (16) 85-94 10
      end
 
 
 
c------------------------------------------------------------------
c
c this routine takes the parametrized model and explodes into the
c full-blown model, which gives the charge that each trap affects and
c the exact amount of charge released after each parallel transfer.
c
c
      subroutine setup_cte_w(q_w,dpde_w,tprof_w,rprof_wt,cprof_wt,Ws,
     .                       DOLOG)
      implicit none
 
      integer           q_w(_WDIM_)     ! output: the run of charge with level #L
      real           dpde_w(_WDIM_)     ! output: the run of charge loss with level #L
      integer       tprof_w(_WDIM_)     ! output: the length of trail for charge level #L
      real         rprof_wt(_WDIM_,100) ! output: the emission probability as fn of downhill pixel
      real         cprof_wt(_WDIM_,100) ! output: the cumulative probability cprof_t( 0001 ) = 1.000-rprof_t(1)
      integer      Ws                   ! output: the number of traps
      logical      DOLOG                ! should the routine output log?
 
c
c-----------------------------------------------------------------------------------------------------------
c
      integer q1c2_u(2,_UDIM_)
      common /q1c2_u_ /q1c2_u           ! cumulative traps
 
      real    chg_leak(5,16)
      common /chg_leak_/chg_leak
c
c-----------------------------------------------------------------------------------------------------------
c
      integer U, UU, W
      integer  q_u(_UDIM_)
      real    lq_u(_UDIM_)
      integer  c_u(_UDIM_)
      real    lc_u(_UDIM_)
 
      real    lq_w(_WDIM_)
      real    f, lf, fr
      real    lq, lw
      integer r
      integer t
      integer n
 
      real    rprof_rt(5,100)
      real    cprof_rt(5,100)
      real*8  rtot
 
      write(*,*)
      write(*,*)
      write(*,'(10x,''#-------------------------------------------'')')
      write(*,'(10x,''#    PARAMETRIZED TRAP DISTRIBUTION LIST    '')')
      write(*,'(10x,''#-------------------------------------------'')')
      write(*,121)
      write(*,122)
      do U = 1, _UDIM_
         q_u(U) = q1c2_u(1,U)
         c_u(U) = q1c2_u(2,U)
        lq_u(U) = log10(q_u(u)*1.0)
        lc_u(U) = log10(c_u(u)*1.0)
        if (q_u(U).eq.0) lq_u(U) = -1
        if (c_u(U).eq.0) lc_u(U) = -1
         write(*,123) U,q_u(U),c_u(U),lq_u(U),lc_u(U)
  121    format(10x,'#',' U ',5x,' qlev',    1x,'  cum',
     .                        5x,'lg10(qlv)',1x,'lg10(cum)')
  122    format(10x,'#','---',5x,'-----',    1x,'-----',
     .                        5x,'---------',1x,'---------')
  123    format(10x,1x,i3.3,  5x,   i5,      1x,i5,
     .                        5x,  f9.5,     1x,f9.5)
         enddo
      write(*,122)
      write(*,*)
 
 
c--------------------------------------------
c
c go from the parametrized cumulative list to
c the location of the individual traps ; just
c a log-interpolation of the above
c
      Ws = c_u(_UDIM_)
      if (Ws.gt._WDIM_) stop 'Ws.ge._WDIM_'
      do W = 1, Ws
         lw = log10(w*1.0)
         uu = 1
         do U = 1, _UDIM_-1
            if (w.ge.c_u(U)) uu = u
            enddo
         f = (lw-lc_u(uu))*1.00/(lc_u(uu+1)-lc_u(uu))
         lq_w(w) = lq_u(uu) + f*(lq_u(uu+1)-lq_u(uu))
          q_w(w) = int(10**(lq_w(w))+0.99)
         if (q_w(w).gt.99999) q_w(w) = 99999
         enddo
 
 
c--------------------------------------------------------
c
c now, take the parametrized 16-point trail distribution
c and populate it into the full 100-point array ; this is
c just simple linear interpolation so it could probably
c be done better...  we go from chg_leak(1:5,1:016) to
c                               rprof_rt(1:5,1:100)
c
      do r = 1, 5
         rprof_rt(r,001) = 1.000*chg_leak(r,01)
         rprof_rt(r,002) = 1.000*chg_leak(r,02)
         rprof_rt(r,003) = 1.000*chg_leak(r,03)
         rprof_rt(r,004) = 0.500*chg_leak(r,03) + 0.500*chg_leak(r,04)
         rprof_rt(r,005) = 1.000*chg_leak(r,04)
         rprof_rt(r,006) = 0.666*chg_leak(r,04) + 0.334*chg_leak(r,05)
         rprof_rt(r,007) = 0.334*chg_leak(r,04) + 0.666*chg_leak(r,05)
         rprof_rt(r,008) = 1.000*chg_leak(r,05)
         rprof_rt(r,009) = 0.750*chg_leak(r,05) + 0.250*chg_leak(r,06)
         rprof_rt(r,010) = 0.500*chg_leak(r,05) + 0.500*chg_leak(r,06)
         rprof_rt(r,011) = 0.250*chg_leak(r,05) + 0.750*chg_leak(r,06)
         rprof_rt(r,012) = 1.000*chg_leak(r,06)
         rprof_rt(r,013) = 0.750*chg_leak(r,06) + 0.250*chg_leak(r,07)
         rprof_rt(r,014) = 0.500*chg_leak(r,06) + 0.500*chg_leak(r,07)
         rprof_rt(r,015) = 0.250*chg_leak(r,06) + 0.750*chg_leak(r,07)
         rprof_rt(r,016) = 1.000*chg_leak(r,07)
         rprof_rt(r,017) = 0.750*chg_leak(r,07) + 0.250*chg_leak(r,08)
         rprof_rt(r,018) = 0.500*chg_leak(r,07) + 0.500*chg_leak(r,08)
         rprof_rt(r,019) = 0.250*chg_leak(r,07) + 0.750*chg_leak(r,08)
         rprof_rt(r,020) = 1.000*chg_leak(r,08)
         rprof_rt(r,021) = 0.800*chg_leak(r,08) + 0.200*chg_leak(r,09)
         rprof_rt(r,022) = 0.600*chg_leak(r,08) + 0.400*chg_leak(r,09)
         rprof_rt(r,023) = 0.400*chg_leak(r,08) + 0.600*chg_leak(r,09)
         rprof_rt(r,024) = 0.200*chg_leak(r,08) + 0.800*chg_leak(r,09)
         rprof_rt(r,025) = 1.000*chg_leak(r,09)
         rprof_rt(r,026) = 0.800*chg_leak(r,09) + 0.200*chg_leak(r,10)
         rprof_rt(r,027) = 0.600*chg_leak(r,09) + 0.400*chg_leak(r,10)
         rprof_rt(r,028) = 0.400*chg_leak(r,09) + 0.600*chg_leak(r,10)
         rprof_rt(r,029) = 0.200*chg_leak(r,09) + 0.800*chg_leak(r,10)
         rprof_rt(r,030) = 1.000*chg_leak(r,10)
         rprof_rt(r,031) = 0.900*chg_leak(r,10) + 0.100*chg_leak(r,11)
         rprof_rt(r,032) = 0.800*chg_leak(r,10) + 0.200*chg_leak(r,11)
         rprof_rt(r,033) = 0.700*chg_leak(r,10) + 0.300*chg_leak(r,11)
         rprof_rt(r,034) = 0.600*chg_leak(r,10) + 0.400*chg_leak(r,11)
         rprof_rt(r,035) = 0.500*chg_leak(r,10) + 0.500*chg_leak(r,11)
         rprof_rt(r,036) = 0.400*chg_leak(r,10) + 0.600*chg_leak(r,11)
         rprof_rt(r,037) = 0.300*chg_leak(r,10) + 0.700*chg_leak(r,11)
         rprof_rt(r,038) = 0.200*chg_leak(r,10) + 0.800*chg_leak(r,11)
         rprof_rt(r,039) = 0.100*chg_leak(r,10) + 0.900*chg_leak(r,11)
         rprof_rt(r,040) = 1.000*chg_leak(r,11)
         rprof_rt(r,041) = 0.900*chg_leak(r,11) + 0.100*chg_leak(r,12)
         rprof_rt(r,042) = 0.800*chg_leak(r,11) + 0.200*chg_leak(r,12)
         rprof_rt(r,043) = 0.700*chg_leak(r,11) + 0.300*chg_leak(r,12)
         rprof_rt(r,044) = 0.600*chg_leak(r,11) + 0.400*chg_leak(r,12)
         rprof_rt(r,045) = 0.500*chg_leak(r,11) + 0.500*chg_leak(r,12)
         rprof_rt(r,046) = 0.400*chg_leak(r,11) + 0.600*chg_leak(r,12)
         rprof_rt(r,047) = 0.300*chg_leak(r,11) + 0.700*chg_leak(r,12)
         rprof_rt(r,048) = 0.200*chg_leak(r,11) + 0.800*chg_leak(r,12)
         rprof_rt(r,049) = 0.100*chg_leak(r,11) + 0.900*chg_leak(r,12)
         rprof_rt(r,050) = 1.000*chg_leak(r,12)
         rprof_rt(r,051) = 0.900*chg_leak(r,12) + 0.100*chg_leak(r,13)
         rprof_rt(r,052) = 0.800*chg_leak(r,12) + 0.200*chg_leak(r,13)
         rprof_rt(r,053) = 0.700*chg_leak(r,12) + 0.300*chg_leak(r,13)
         rprof_rt(r,054) = 0.600*chg_leak(r,12) + 0.400*chg_leak(r,13)
         rprof_rt(r,055) = 0.500*chg_leak(r,12) + 0.500*chg_leak(r,13)
         rprof_rt(r,056) = 0.400*chg_leak(r,12) + 0.600*chg_leak(r,13)
         rprof_rt(r,057) = 0.300*chg_leak(r,12) + 0.700*chg_leak(r,13)
         rprof_rt(r,058) = 0.200*chg_leak(r,12) + 0.800*chg_leak(r,13)
         rprof_rt(r,059) = 0.100*chg_leak(r,12) + 0.900*chg_leak(r,13)
         rprof_rt(r,060) = 1.000*chg_leak(r,13)
         rprof_rt(r,061) = 0.900*chg_leak(r,13) + 0.100*chg_leak(r,14)
         rprof_rt(r,062) = 0.800*chg_leak(r,13) + 0.200*chg_leak(r,14)
         rprof_rt(r,063) = 0.700*chg_leak(r,13) + 0.300*chg_leak(r,14)
         rprof_rt(r,064) = 0.600*chg_leak(r,13) + 0.400*chg_leak(r,14)
         rprof_rt(r,065) = 0.500*chg_leak(r,13) + 0.500*chg_leak(r,14)
         rprof_rt(r,066) = 0.400*chg_leak(r,13) + 0.600*chg_leak(r,14)
         rprof_rt(r,067) = 0.300*chg_leak(r,13) + 0.700*chg_leak(r,14)
         rprof_rt(r,068) = 0.200*chg_leak(r,13) + 0.800*chg_leak(r,14)
         rprof_rt(r,069) = 0.100*chg_leak(r,13) + 0.900*chg_leak(r,14)
         rprof_rt(r,070) = 1.000*chg_leak(r,14)
         rprof_rt(r,071) = 0.900*chg_leak(r,14) + 0.100*chg_leak(r,15)
         rprof_rt(r,072) = 0.800*chg_leak(r,14) + 0.200*chg_leak(r,15)
         rprof_rt(r,073) = 0.700*chg_leak(r,14) + 0.300*chg_leak(r,15)
         rprof_rt(r,074) = 0.600*chg_leak(r,14) + 0.400*chg_leak(r,15)
         rprof_rt(r,075) = 0.500*chg_leak(r,14) + 0.500*chg_leak(r,15)
         rprof_rt(r,076) = 0.400*chg_leak(r,14) + 0.600*chg_leak(r,15)
         rprof_rt(r,077) = 0.300*chg_leak(r,14) + 0.700*chg_leak(r,15)
         rprof_rt(r,078) = 0.200*chg_leak(r,14) + 0.800*chg_leak(r,15)
         rprof_rt(r,079) = 0.100*chg_leak(r,14) + 0.900*chg_leak(r,15)
         rprof_rt(r,080) = 1.000*chg_leak(r,15)
         rprof_rt(r,081) = 0.900*chg_leak(r,15) + 0.100*chg_leak(r,16)
         rprof_rt(r,082) = 0.800*chg_leak(r,15) + 0.200*chg_leak(r,16)
         rprof_rt(r,083) = 0.700*chg_leak(r,15) + 0.300*chg_leak(r,16)
         rprof_rt(r,084) = 0.600*chg_leak(r,15) + 0.400*chg_leak(r,16)
         rprof_rt(r,085) = 0.500*chg_leak(r,15) + 0.500*chg_leak(r,16)
         rprof_rt(r,086) = 0.400*chg_leak(r,15) + 0.600*chg_leak(r,16)
         rprof_rt(r,087) = 0.300*chg_leak(r,15) + 0.700*chg_leak(r,16)
         rprof_rt(r,088) = 0.200*chg_leak(r,15) + 0.800*chg_leak(r,16)
         rprof_rt(r,089) = 0.100*chg_leak(r,15) + 0.900*chg_leak(r,16)
         rprof_rt(r,090) = 1.000*chg_leak(r,16)
         rprof_rt(r,091) = 0.900*chg_leak(r,16)
         rprof_rt(r,092) = 0.800*chg_leak(r,16)
         rprof_rt(r,093) = 0.700*chg_leak(r,16)
         rprof_rt(r,094) = 0.600*chg_leak(r,16)
         rprof_rt(r,095) = 0.500*chg_leak(r,16)
         rprof_rt(r,096) = 0.400*chg_leak(r,16)
         rprof_rt(r,097) = 0.300*chg_leak(r,16)
         rprof_rt(r,098) = 0.200*chg_leak(r,16)
         rprof_rt(r,099) = 0.100*chg_leak(r,16)
         rprof_rt(r,100) = 0.000*chg_leak(r,16)
         enddo
 
 
c-----------------------------------------------------------------------
c
c the rprof() array gives the fraction of the trapped charge that
c    comes out at every parallel shift; we need to normalize this
c    to 1.00
c we then need to compute the cumulative distribution cprof(), which
C    tells us how much is left
c
      do r = 1, 5
         rtot = 0.
         do t = 001, 100
            rtot = rtot + rprof_rt(r,t)
            enddo
         do t = 001, 100
            rprof_rt(r,t) = rprof_rt(r,t)/rtot
            enddo
         rtot = 0.
         do t = 001, 100
            rtot = rtot + rprof_rt(r,t)
            cprof_rt(r,t) = 1-rtot
            enddo
         enddo
 
      write(*,*)
      write(*,*)
      write(*,300)
      write(*,301)
      write(*,300)
      write(*,302)
      write(*,303)
      do n = 1, 17
         if (n.eq.01) t = 001
         if (n.eq.02) t = 002
         if (n.eq.03) t = 003
         if (n.eq.04) t = 005
         if (n.eq.05) t = 008
         if (n.eq.06) t = 012
         if (n.eq.07) t = 016
         if (n.eq.08) t = 020
         if (n.eq.09) t = 025
         if (n.eq.10) t = 030
         if (n.eq.11) t = 040
         if (n.eq.12) t = 050
         if (n.eq.13) t = 060
         if (n.eq.14) t = 070
         if (n.eq.15) t = 080
         if (n.eq.16) t = 090
         if (n.eq.17) t = 100
         write(*,310) n,t,(rprof_rt(r,t),r=1,5),
     .                    (cprof_rt(r,t),r=1,5)
         enddo
  300 format(10x,'#',105('-'))
  301 format(10x,'#','  ',1x,'   ',
     .           5x,'RADIAL PROFILE OF RELEASE                    ',
     .           5x,'CUMULATIVE DISTRIBUTION REMAINING            ')
  302 format(10x,'#',' N',1x,' T ',
     .           2(5x,'  q=1      q=10     q=100    q=1000  q=10000 '))
  303 format(10x,'#','--',1x,'---',
     .           2(5x,'-------- -------- -------- -------- -------- '))
  310 format(10x,1x,i2.2,1x,i3.3, 5x,5(f8.6,1x),5x,5(f8.6,1x))
      write(*,303)
      write(*,*)
 
c-----------------------------------------------------------------------
c
c need to populate the full array now:
c
c           rprof_rt(01:05,001:100)
c      ---> rprof_wt(01:Ws,001:100)
c
c
      do W = 1, Ws
         R = 1
         lq = log10(q_w(W)*1.0)
         fr = (q_w(W)-1)/(10-1)
         if (q_w(w).ge.00010) then
            R = 2
            fr = (lq-1)/(2-1)
            endif
         if (q_w(w).ge.00100) then
            R = 3
            fr = (lq-2)/(3-2)
            endif
         if (q_w(w).ge.01000) then
            R = 4
            fr = (lq-3)/(3-2)
            endif
         if (q_w(w).ge.10000) then
            R = 4
            fr = 1.00
            endif
         do T = 1, 100
            rprof_wt(W,T) = rprof_rt(R,T) + fr*(rprof_rt(R+1,T)
     .                                         -rprof_rt(R  ,T))
            cprof_wt(W,T) = cprof_rt(R,T) + fr*(cprof_rt(R+1,T)
     .                                         -cprof_rt(R  ,T))
            enddo
         enddo
 
 
 
      if (DOLOG) then
         open(99,file='INFO_W.RQPROF',status='unknown')
         write(99,'(''# '')')
         write(99,'(''# '',234(''*''))')
         write(99,'(''# ***** '')')
         write(99,'(''# ***** SHOW FINAL TRAPS AND RELEASE PROFILES'')')
         write(99,'(''# ***** '')')
         write(99,'(''# '',234(''*''))')
         write(99,'(''#   '')')
         write(99,'(''# '')')
         write(99,198)
         write(99,199)
         write(99,198)
  198    format('#','---',5x,'------',5x,36(' -----'))
  199    format('#','  W',5x,'  qlev',
     .                    5x,'   T=1   T=2   T=3   T=4   T=5',
     .                       '   T=6   T=7   T=8   T=9  T=10',
     .                       '  T=11  T=12  T=13  T=14  T=15',
     .                       '  T=16  T=17  T=18  T=19  T=20',
     .                       '  T=25  T=30  T=35  T=40  T=45',
     .                       '  T=50  T=55  T=60  T=65  T=70',
     .                       '  T=75  T=80  T=85  T=90  T=95',
     .                       ' T=100')
         do W = 1, Ws
            write(99,'(1x,i3.3,5x,i6.6,5x,40i6)')
     .            W,q_w(W),(int(rprof_wt(w,t)*1e5),t=001,020,001),
     .                     (int(rprof_wt(w,t)*1e5),t=025,100,005)
            if (W.eq.W/25*25.and.W.ne.Ws) then
               write(99,198)
               write(99,199)
               write(99,198)
               endif
            enddo
         write(99,198)
         write(99,199)
         write(99,198)
         write(99,'(''# '')')
         write(99,'(''# '')')
         write(99,'(''# '')')
         write(99,'(''# '')')
         write(99,'(''# '')')
         write(99,'(''# '',234(''*''))')
         write(99,'(''# ***** '')')
         write(99,'(''# ***** SHOW TRAPS AND CUMULATIVE PROFILES'')')
         write(99,'(''# ***** '')')
         write(99,'(''# '',234(''*''))')
         write(99,'(''#   '')')
         write(99,198)
         write(99,199)
         write(99,198)
         do W = 1, Ws
            write(99,'(1x,i3.3,5x,i6.6,5x,40i6)')
     .            W,q_w(W),(int(cprof_wt(w,t)*1e5),t=001,020,001),
     .                     (int(cprof_wt(w,t)*1e5),t=025,100,005)
            if (W.eq.W/25*25.and.W.ne.Ws) then
               write(99,198)
               write(99,199)
               write(99,198)
               endif
            enddo
         write(99,198)
         write(99,199)
         write(99,198)
         close(99)
         endif
 
c----------------------------------------------------------------
c
c set it up so that every trap has exactly 1 electron it can grab
c in previous models (ACS) I sometimes dealt either with fractional
c traps or with bunches of traps ; this will be scaled later
c by the overall scaling and perhaps a more detailed column= or
c column+row-based additional scaling.
c
      do W = 1, Ws
         dpde_w(W) = 1.00
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sim_colreadout_l_uvis_w.f"
c****                                         
c*********************************************
                                              
 
c------------------------------------------------------------
c
c This is the workhorse subroutine; it simulates the readout
c of one column pixi() and outputs this to pixo() using a single
c iteration.  It can be called successively to do the transfer
c in steps.
c
      subroutine sim_colreadout_l_uvis_w(pixi,pixo,pixf,J1,J2,JDIM,
     .                                   q_w,dpde_w,NITs,
     .                                   tprof_w,rprof_wt,cprof_wt,Ws)
      implicit none
 
      integer   JDIM
      real      pixi(JDIM)        ! input column array
      real      pixo(JDIM)        ! outout column array
      real      pixf(JDIM)        ! outout column array
      integer   J1, J2
 
      integer    q_w(_WDIM_)      ! the 5 readout-parameter arrays
      real    dpde_w(_WDIM_)
      integer NITs
      integer tprof_w(_WDIM_)
      real   rprof_wt(_WDIM_,100)
      real   cprof_wt(_WDIM_,100)
      integer Ws
 
      integer j, t
 
      real  pix0
 
      real*8  ftrap
      integer ttrap
 
      real fpix ! fraction of this pixel involved
      real fopn ! fraction of this trap that is open
      real ffil ! fraction of this trap that gets filled
      real dpix ! the amount of charge that gets transferred
 
      real*8 padd
      integer w
 
      real*8 pix_1
      real*8 pix_2
      real*8 pix_3
 
      real*8 padd_2
      real*8 padd_3
      real*8 prem_3, prem
      real*8 prem_4
      real*8 pmax, prev
 
      real    fcarry
      real    fcarry0

      fcarry0 = 0.0
 
      if (Ws.gt._WDIM_) stop 'Ws.gt._WDIM_'   ! more traps than we are allowed
 
 
c----------------------------------------
c
c figure out which traps we don't need to
c worry about in this column
c
      pmax = 10.
      do j = 0001, JDIM
         pixo(j) = pixi(j)
         if (pixo(j).gt.pmax) pmax = pixo(j)
         enddo
 
 
c-----------------------------------------------------------
c
c go thru the traps one at a time (from highest to lowest q)
c and see when they get filled and emptied; adjust the
c pixels accordingly
c
      do W = Ws, 001, -1
         if (q_w(W).gt.pmax) goto 333
 
         ftrap =   0.0
         ttrap =  _TDIM_
 
         fcarry = fcarry0
         do j = J1, J2                                  ! go up the column pixel by pixel
            pix_1 = pixo(j)
            if (ttrap.ge.(_TDIM_).and.pix_1.lt.q_w(w)-1) goto 444
            if (pixo(j).ge.0) then
               pix_1 = pixo(j) + fcarry                 ! step 1, shuffle charge in
               fcarry = pix_1 - int(pix_1)
               pix_1  = int(pix_1)
               endif
 
            if (j.gt.J1) then
               if (pixf(j).lt.pixf(j-1))
     .             ftrap = pixf(j)/pixf(j-1)*ftrap
               endif
 
            padd_2 = 0.                                 ! step 2, release the charge
            if (ttrap.lt._TDIM_) then
               ttrap = ttrap + 1
               padd_2 = rprof_wt(w,ttrap)*ftrap
               endif
 
            padd_3 = 0.
            prem_3 = 0.
            if (pix_1.ge.q_w(w)) then
               prem_3 = dpde_w(w)/NITs*pixf(j)
               if (ttrap.lt._TDIM_)
     .             padd_3 = cprof_wt(w,ttrap)*ftrap
               ttrap = 0
               ftrap = prem_3
               endif
            pixo(j) = pixo(j) + padd_2 + padd_3 - prem_3
  444       continue
            enddo!j
  333    continue
         enddo!w
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_raz2rac.f"
c****                                         
c*********************************************
                                              
 
 
c------------------------------------------------------------------------
c
c this routine does the inverse CTE blurring... it takes an observed
c image and generates the image that would be pushed through the readout
c algorithm to generate the observation
c
      subroutine sub_wfc3uv_raz2rac(pixz_raz,pixz_rac,pixz_fff,
     .                              CTE_FF,FIX_ROCRs,
     .                              q_w,dpde_w,tprof_w,
     .                              rprof_wt,cprof_wt,Ws)
 
      implicit none
 
      real      pixz_raz(8412,2070)  ! original image
      real      pixz_rac(8412,2070)  ! corrected image
      real      pixz_fff(8412,2070)  ! corrected image
      real      CTE_FF               ! scaling of CTE correction
      logical   FIX_ROCRs            ! should we make allowance for readout-CRs?
 
      integer         Ws             ! model: number of traps
      integer        q_w(_WDIM_)     ! model: the run of charge with level #L
      real        dpde_w(_WDIM_)     ! model: the run of charge loss with level #L
      integer    tprof_w(_WDIM_)     ! model: the length of trail for charge level #L
      real      rprof_wt(_WDIM_,100) ! model: the emission probability as fn of downhill pixel
      real      cprof_wt(_WDIM_,100) ! model: the cumulative probability cprof_t( 0001 ) = 1.000-rprof_t(1)
c
c-------------------------------------------------------------
c
      real pixe
      integer*4 ival
 
      integer i, ii
      integer n, q, qu
      integer j, jj, t, w, jmax
      real      dcte
 
      logical REDO
      integer NREDO
 
      real    dmod
c
c--------------------------------------
c
      real pix_obsd(2070)
      real pix_modl(2070)
 
      real pix_init(2070)
      real pix_curr(2070)
      real pix_read(2070)
      real pix_ctef(2070)
 
      integer NITCTE, NITCTEs
      integer NITINV, NITINVs
      real*8 aa, bb
 
      logical VERBOSE
      common /VERBOSE_/VERBOSE

      real*8 tot
c
c--------------------------------------
c
 
 
c----------------------------------------------
c
c set up the scaling array
c
      do i = 0001, 8412
      do j = 0001, 2070
         pixz_fff(i,j) = CTE_FF*j/2048.00
         pixz_rac(i,j) = pixz_raz(i,j)
         enddo
         enddo
 
 
 
      NITINVs = _NITERN_
      NITCTEs = _NITCTE_
      do i = 0001, 8412                                               ! go thru all 8412 columns, including the
         tot = 0.
         do j = 0001, 2070                                            !    horizontal pre/post scan
            pix_obsd(j) = pixz_raz(i,j)
            tot = tot + abs(pix_obsd(j))
            enddo
         if (tot.le.1) goto 9998                                      ! skip, no signal in this column
         
         if (VERBOSE)
     .   write(*,2117) i,(int(pix_obsd(j)+1000.5)-1000,j=2020,2060)
         NREDO = 0
 9999    continue ! REDO
         REDO = .false.                                               ! start out not needing to mitigate readout CRs
         do j = 0001, 2070
            pix_modl(j) = pixz_raz(i,j)                               ! start with observed image as model
            pix_ctef(j) = pixz_fff(i,j)                               ! adopt the scaling for this column
            enddo
 2117    format(i5.4,5x,51i6)
         do NITINV = 1, NITINVs
            do j = 0001, 2070
               pix_curr(j) = pix_modl(j)                              ! start with the input array being the last output
               pix_read(j) = pix_modl(j)
               pix_ctef(j) = pixz_fff(i,j)                            ! if we've CR-rescaled, then implement this
               enddo
            do NITCTE = 1, NITCTEs                                    ! take each pixel down the detector in NITCTEs=7 s
               call sim_colreadout_l_uvis_w(pix_curr,pix_read,
     .                                      pix_ctef,0001,2070,2070,
     .                                      q_w,dpde_w,NITCTEs,
     .                                      tprof_w,rprof_wt,
     .                                      cprof_wt,Ws)
               do j = 0001, 2070                                      ! copy the just-read out image into the input imag
                  pix_curr(j) = pix_read(j)
                  enddo
               enddo
            do j = 0001, 2070                                         ! dampen the adjustment if it is close to the
               dmod  = pix_obsd(j)-pix_read(j)                        ! readnoise... this is an additional aid in
               if (NITINV.lt.NITINVs) then                            ! mitigating the impact of readnoise
                  dmod = dmod*(dmod**2/(dmod**2+3.25**2))
                  endif
               pix_modl(j) = pix_modl(j) + dmod                       ! adjust each pixel as we determine best
               enddo
            if (VERBOSE)
     .      write(*,2117) i,(int(pix_modl(j)+1000.5)-1000,j=2020,2060)
            enddo ! NITINV
         if (VERBOSE) then
            write(*,2117) i,(int(pix_modl(j)+1000.5)-1000,j=2020,2060)
            write(*,*)
            write(*,2117) i,(int(pix_read(j)+1000.5)-1000,j=2020,2060)
            write(*,2117) i,(int(pix_obsd(j)+1000.5)-1000,j=2020,2060)
            write(*,'(256(''-''))')
            write(*,2117) i,(j,j=2020,2060)
            write(*,'(256(''-''))')
            endif
         if (FIX_ROCRs) then                                         ! look for and down-scale the CTE model if
         do j = 0011, 2070-2                                         ! we find the tell-tale sign of readout CRs
            if (((pix_modl(j).lt.-10).and.                           ! being oversubtracted; if we find any, then
     .           (pix_modl(j)-pix_obsd(j).lt.-10)).or.               ! go back up and rerun this column
     .          ((pix_modl(j)+pix_modl(j+1).lt.-12).and.
     .           (pix_modl(j)+pix_modl(j+1)
     .           -pix_obsd(j)-pix_obsd(j+1).lt.-12)).or.
     .          ((pix_modl(j)+pix_modl(j+1)+pix_modl(j+2).lt.-15).and.
     .           (pix_modl(j)+pix_modl(j+1)+pix_modl(j+2)
     .           -pix_obsd(j)-pix_obsd(j+1)-pix_obsd(j+2).lt.-15))) then
                jmax = j
                do jj = j-10,j                                       ! go downstream and look for the offending CR
                   if (pix_modl(jj  )-pix_obsd(jj  ).gt.             !
     .                 pix_modl(jmax)-pix_obsd(jmax)) then
                       jmax = jj
                       endif
                   enddo
                do jj = jmax, j                                      ! downgrade the CR's scaling and also for those
                   pixz_fff(i,jj) = pixz_fff(i,jj)*0.75              ! between the oversubtracted pixel and it
                   enddo
                REDO = .true.
                endif
            enddo
            endif
         if (REDO) then
             NREDO = NREDO + 1
             if (NREDO.lt.5) goto 9999
             endif
         do j = 0001, 2070
            pixz_rac(i,j) = pix_modl(j)
            enddo
         if (.not.VERBOSE) then
            ii = i-(i-1)/2103*2103
            if (i.eq.0001) then
               write(*,*)
               write(*,'(5x,100(''*''))')
               write(*,'(5x,005(''*''),'' AMPLIFIER C'')')
               write(*,'(5x,100(''*''))')
               write(*,*)
               endif
            if (i.eq.2104) then
               write(*,*)
               write(*,'(5x,100(''*''))')
               write(*,'(5x,005(''*''),'' AMPLIFIER D'')')
               write(*,'(5x,100(''*''))')
               write(*,*)
               endif
            if (i.eq.4207) then
               write(*,*)
               write(*,'(5x,100(''*''))')
               write(*,'(5x,005(''*''),'' AMPLIFIER A'')')
               write(*,'(5x,100(''*''))')
               write(*,*)
               endif
            if (i.eq.6310) then
               write(*,*)
               write(*,'(5x,100(''*''))')
               write(*,'(5x,005(''*''),'' AMPLIFIER B'')')
               write(*,'(5x,100(''*''))')
               write(*,*)
               endif
            if (ii.eq.0000+0001.or.
     .          ii.eq.0025+0001.or.
     .          ii.eq.0025+2049.or.
     .          (ii-26).eq.(ii-26)/0064*0064) then
               write(*,2126)
               write(*,2125) 'ORIGINAL  ', 'CORRECTED ', '  CHANGE  '
               write(*,2126)
               write(*,2128) (j,j=1995,2005), (j,j=1995,2005),
     .                       (j,j=1995,2005)
               write(*,2126)
               endif
            write(*,2127) i,((int(pix_obsd(j)+100.5)-100),j=1995,2005),
     .                      ((int(pix_modl(j)+100.5)-100),j=1995,2005),
     .                      ((int(pix_modl(j)+100.5)-100)
     .                      -(int(pix_obsd(j)+100.5)-100),j=1995,2005)
 2125       format(5x,4x,3(5x,28x,a10,28x))
 2126       format(5x,'----',3(5x,11('------')))
 2127       format(5x,i4.4,3(5x,11i6))
 2128       format(5x,'ICOL',3(5x,'J=',i4,10i6))
            endif
 9998    continue
         enddo!i
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_read_raw.f"
c****                                         
c*********************************************
                                              
 
 
c---------------------------------------------------------------------
c
c This routine reads in a _raw.fits image and converts into a convenient
c 'z' format (concatenated horizontallly with readout down and to the left)
c
c At present, it can do this for full-frame and a *few* subarrays; no
c guarantee how well the correction will work on subarrays, as the readout
c timing may be somewhat different.  For the subarrays, it will pad the
c pre-scan and unused pixels to make it look like a regular image
c
      subroutine sub_wfc3uv_read_raw(FILEI,pixz_raw)
      implicit none
 
      character*80 FILEI
      real*4 pixz_raw(8412,2070)
 
      integer*2 pix1(4206,2070)
      integer*2 pix4(4206,2070)
      integer*2 pixa(2070,2050)
      integer*2 pixb(4142,2050)
      integer*2 pixc(1048,1024)
      integer*2 pixd(0536,0512)
 
      character*80 STRING_HEAD(360)
      integer i, j
      character*20 APERTURE
      character*4  CCDAMP
      integer h, k
      integer NREPLACE
      integer Ls, Lu
      real    pl(41400), pbar, psig
 
      print*,' '
      print*,'          ENTER wfc3uv_read_raw: ',FILEI(1:20)
 
      do i = 0001, 8412
      do j = 0001, 2070
         pixz_raw(i,j) = -999
         enddo
         enddo


 
      call fitshead2string(FILEI,STRING_HEAD)
      APERTURE = 'NONE'
      CCDAMP   = 'NONE'
      do h = 001, 360
         if (STRING_HEAD(h)(01:10).eq.'APERTURE= ')
     .       read(STRING_HEAD(h)(11:30),*) APERTURE
         if (STRING_HEAD(h)(01:10).eq.'CCDAMP  = ')
     .       read(STRING_HEAD(h)(11:30),*) CCDAMP
         enddo
      print*,'          CCDAMP         : ',CCDAMP
      print*,'          APERTURE       : ',APERTURE
      print*,'          APERTURE(01:01): ',APERTURE(01:01)
      print*,'          APERTURE(02:12): ',APERTURE(02:12)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      print*,'          APERTURE(01:12): ',APERTURE(01:12)
      if (CCDAMP.eq.'ABCD') then
      if (APERTURE(01:06).eq.'UVIS  '.or.
     .    APERTURE(01:06).eq.'UVIS1 '.or.
     .    APERTURE(01:06).eq.'UVIS2 '.or.
     .    APERTURE(01:09).eq.'UVIS-FIX '.or.
     .    APERTURE(01:09).eq.'UVIS1-FIX'.or.
     .    APERTURE(01:09).eq.'UVIS2-FIX'.or.
     .    APERTURE(01:09).eq.'G280-REF '.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD'.or.
     .    APERTURE(01:11).eq.'UVIS-CENTER'.or.
     .    APERTURE(01:11).eq.'UVIS-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS1-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS2-IR-FIX'.or.
     .    APERTURE(01:13).eq.'UVIS-QUAD-FIX') then
          print*,'                               : [1] UVIS2'
          call readfits_i2e(FILEI,pix1,4206,2070,1)
          do i = 0001, 2103
          do j = 0001, 2070
             pixz_raw(i+0*2103,j) = pix1(i+0000,j+0000) + 32768.
             pixz_raw(i+1*2103,j) = pix1(4207-i,j+0000) + 32768.
             enddo
             enddo
          print*,'                               : [4] UVIS1'
          call readfits_i2e(FILEI,pix4,4206,2070,4)
          do i = 0001, 2103
          do j = 0001, 2070
             pixz_raw(i+2*2103,j) = pix4(i+0000,2071-j) + 32768.
             pixz_raw(i+3*2103,j) = pix4(4207-i,2071-j) + 32768.
             enddo
             enddo
          goto 1
          endif
          endif




 
      if (CCDAMP.eq.'A   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2A-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_i2e(FILEI,pixa,2070,2050,1)
          do i = 0001, 2070
          do j = 0001, 2050
             pixz_raw(2+i+2*2103,2051-j+1) = pixa(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif
          endif
 
      if (CCDAMP.eq.'B   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2B-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_i2e(FILEI,pixa,2070,2050,1)
          do i = 0001, 2070
          do j = 0001, 2050
             pixz_raw(2071-i+3*2103+2,2051-j+1) = pixa(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif
          endif
 
      if (CCDAMP.eq.'C   ') then
      if (APERTURE(01:14).eq.'UVIS2-2K2C-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_i2e(FILEI,pixa,2070,2050,1)
          do i = 0001, 2070
          do j = 0001, 2050
             pixz_raw(2+i+0*2103,j+1) = pixa(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif
          endif
 
      if (APERTURE(01:13).eq.'UVIS1-2K4-SUB') then
          call readfits_i2e(FILEI,pixb,4142,2050,1)
          do i = 0001, 2071
          do j = 0001, 2050
             pixz_raw(0002+i+2*2103,2052-j) = pixb(i,j) + 32768.
             enddo
             enddo
          do i = 2072, 4119
          do j = 0001, 2050
             pixz_raw(026+(4119-i)+3*2103,2052-j) = pixb(i,j) + 32768.
             enddo
             enddo
          do i = 0001, 0023  ! fake the pre-scan
          do j = 0001, 2050
             pixz_raw(0002+i+3*2103,2052-j) = pixb(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C1K1C-SUB') then
          call readfits_i2e(FILEI,pixc,1048,1024,1)
          do i = 0001, 1048
          do j = 0001, 1024
             pixz_raw(2+i+0*2103,j+1) = pixc(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif
 

      if (APERTURE(01:15).eq.'UVIS2-C512C-SUB') then
          call readfits_i2e(FILEI,pixd,536,512,1)
          do i = 0001, 0536
          do j = 0001, 0512
             pixz_raw(2+i+0*2103,j+1) = pixd(i,j) + 32768.
             enddo
             enddo
          goto 1
          endif

      if (APERTURE(01:15).eq.'UVIS2-C512D-SUB') then
          call readfits_i2e(FILEI,pixd,536,512,1)
          do i = 0001, 0536
          do j = 0001, 0512
             pixz_raw(2+i+1*2103,j+1) = pixd(537-i,j) + 32768.
             enddo
             enddo
          goto 1
          endif

      if (APERTURE(01:15).eq.'UVIS1-C512A-SUB') then
          call readfits_i2e(FILEI,pixd,536,512,1)
          do i = 0001, 0536
          do j = 0001, 0512
             pixz_raw(2+i+2*2103,j+1) = pixd(i,513-j) + 32768.
             enddo
             enddo
          goto 1
          endif

      if (APERTURE(01:15).eq.'UVIS1-C512B-SUB') then
          call readfits_i2e(FILEI,pixd,536,512,1)
          do i = 0001, 0536
          do j = 0001, 0512
             pixz_raw(2+i+3*2103,j+1) = pixd(537-i,513-j) + 32768.
             enddo
             enddo
          goto 1
          endif

      print*,'PROBLEM in sub_wfc3uv_read_raw'
      print*,'   APERTURE NOT FOUND: '
      print*,'             APERTURE: ',APERTURE
      print*,'               CCDAMP: ',CCDAMP
      stop
  
 
 
c-----------------------------------------------------------------
c
c come here when all the good pixels have been read in ;
c we will make an attempt to populate the pre-scan and other
c pixels with seemingly legitimate values, just so that my
c algorithm can operate on them; try various ways to
c fill these pixels, starting with using values in the
c same amp, then same chip...
c
    1 continue

      if (.true.) return

      NREPLACE = 0
      do k = 1, 4                ! next try using values in the same amp
         Ls = 0
         do j = 0001, 2070
            do i = 0020, 0024
               if (pixz_raw(i+(k-1)*2103,j).gt.-9999) then
                  Ls = Ls + 1
                  if (Ls.gt.41400) stop 'Ls.gt.41400'
                  pl(Ls) = pixz_raw(i+(k-1)*2103,j)
                  endif
               enddo
            enddo
         if (Ls.gt.0) then
            call barsig(pl,Ls,pbar,psig,Lu)
            print*,'-----> k: ',k,pbar,psig,Ls,Lu
            do j = 0001, 2070
            do i = 0001, 2103
               if (pixz_raw(i+(k-1)*2103,j).lt.-9999) then
                   pixz_raw(i+(k-1)*2103,j) = pbar
                   NREPLACE = NREPLACE+1
                   endif
               enddo
               enddo
            endif
         enddo
      print*,' REPLACE1: ',NREPLACE
      NREPLACE = 0
      Ls = 0
      do k = 1, 4                ! next try using any reasonable blev value to fill
         do j = 0001, 2070
            do i = 0020, 0024
               if (pixz_raw(i+(k-1)*2103,j).gt.-99990) then
                  Ls = Ls + 1
                  if (Ls.gt.41400) stop 'Ls.gt.41400'
                  pl(Ls) = pixz_raw(i+(k-1)*2103,j)
                  endif
               enddo
            enddo
         enddo
      if (Ls.gt.0) then
         call barsig(pl,Ls,pbar,psig,Lu)
         print*,'----->  : ',0,pbar,psig,Ls,Lu
         do k = 1, 4
            do j = 0001, 2070
            do i = 0001, 2103
               if (pixz_raw(i+(k-1)*2103,j).lt.-99990) then
                   pixz_raw(i+(k-1)*2103,j) = pbar
                   NREPLACE = NREPLACE+1
                   endif
               enddo
               enddo
            enddo
         endif
      print*,' REPLACE2: ',NREPLACE
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_raw2raz.f"
c****                                         
c*********************************************
                                              
 
c-------------------------------------------------
c
c Does the blev correction to go from a raw image
c in DNs to a raz image in electrons
c (GAIN=1.5 is hardcoded)
c
      subroutine sub_wfc3uv_raw2raz(pixz_raw,pixz_raz)
      implicit none
 
      real*4 pixz_raw(8412,2070)
      real*4 pixz_raz(8412,2070)
 
      character*80 FILEI
      character*80 FILEO
 
 
      integer NARG, NARGs
      integer i, j, k
      integer ii,jj
 
      integer Ls, Lu, L
      real pl(9999)
      real bar, sig
 
      real colbar(25), colbarbar
      real colsig(25)
      integer colnnn(25)
      integer coluuu(25)
      real biask(4)
 
      real plist(12420)
 
      real bs_ik, rclip
 
      character ampk(4)
      common /ampk_/ampk
      data ampk/'C','D','A','B'/
 
      logical VERBOSE
      common /VERBOSE_/VERBOSE
c
c------------------------------------------------------
c
 
      print*,'                                                      '
      print*,'    ENTER wfc3uv_raw2raz (essentially blevcor)        '
      print*,'                                                      '
      print*,'          GOAL: use the pre-scan pixels to            '
      print*,'                determine the background bias level   '
      print*,'                for each amplifier so that it can     '
      print*,'                be properly subtracted.  I first      '
      print*,'                find the settle-down profile for      '
      print*,'                each amp, subtract it, then I measure '
      print*,'                the bias level from pixels that are   '
      print*,'                within region [20:25,0001:2051]       '
      print*,'                                                      '
 
 
c------------------------------------------------------
c
c go through amp by amp, determine the bias level,
c and subtract it
c
 
 
      write(*,110)
      write(*,111) (i,i=1,25)
      write(*,110)
      do k = 1, 4
         do i = 01, 25
            Ls = 0
            do j = 0001, 2048
               if (pixz_raw(i+(k-1)*2103,j).gt.0) then
                  Ls = Ls + 1
                  plist(Ls) = pixz_raw(i+(k-1)*2103,j)
                  endif
               enddo
            call barsig(plist,Ls,bar,sig,Lu)
            colbar(i) = bar
            colsig(i) = sig
            colnnn(i) = Ls
            coluuu(i) = Lu
            enddo
         colbarbar = (colbar(20)+colbar(21)+colbar(22)
     .               +colbar(23)+colbar(24)+colbar(25))/6.0
         write(*,112) k,ampk(k),'AVG',(rclip(colbar(i)
     .                                      -colbarbar,-999.,999.),
     .                                       i=1,25)
         write(*,112) k,ampk(k),'RMS',(colsig(i),i=1,25)
         if (VERBOSE) then
            write(*,113) k,ampk(k),'TOT',(colnnn(i),i=1,25)
            write(*,113) k,ampk(k),'USE',(coluuu(i),i=1,25)
            endif
  110    format(5x,1x,1x,3x,1x,1x,3x,1x,25(' ------'))
  111    format(5x,1x,1x,3x,1x,1x,3x,1x,25(' i=',i4.4))
  112    format(5x,i1,1x,'AMP',a1,1x,a3,1x,25f7.2)
  113    format(5x,i1,1x,'AMP',a1,1x,a3,1x,25i7)
         print*,' '
         Ls = 0
         do i = 20, 25
            do j = 0001, 2070
               if (pixz_raw(i+(k-1)*2103,j).gt.0) then
                  Ls = Ls + 1
                  plist(Ls) = pixz_raw(i+(k-1)*2103,j)
                  endif
               enddo
            enddo
         call barsig(plist,Ls,bar,sig,Lu)
         biask(k) = bar
         do i = 0001, 2103                             ! correct blev for pixels
         do j = 0001, 2070                             !   in this amp
            pixz_raz(i+(k-1)*2103,j) =
     .      pixz_raw(i+(k-1)*2103,j) - biask(k)
            enddo
            enddo
         do i = 0001, 0025                             ! correct the prescan for
         do j = 0001, 2070                             !    onset horiz gradient
            pixz_raz(i+(k-1)*2103,j) =
     .      pixz_raz(i+(k-1)*2103,j) - (colbar(i)-colbarbar)
            enddo
            enddo
         enddo
      print*,'                                  '
 
 
c------------------------------------------------------
c
c multiply by the gain
c
      print*,'    MULTIPLY BY GAIN=1.5'
      do i = 0001, 2103
      do j = 0001, 2070
         pixz_raz(i+0000,j) = 1.5000*pixz_raz(i+0*2103,j)
         pixz_raz(i+2103,j) = 1.5000*pixz_raz(i+1*2103,j)
         pixz_raz(i+4206,j) = 1.5000*pixz_raz(i+2*2103,j)
         pixz_raz(i+6309,j) = 1.5000*pixz_raz(i+3*2103,j)
         enddo
         enddo
 
 
c------------------------------------------------------
c
c correct for the horizontal bias gradient
c
      print*,'    CORRECT HORIZONTAL BIAS GRADIENT'
      do k = 1, 4
         do i = 0001, 2103
         do j = 0001, 2070
            pixz_raz(i+(k-1)*2103,j) =
     .      pixz_raz(i+(k-1)*2103,j) - bs_ik(i,1)
            enddo
            enddo
         enddo
 
 
c------------------------------------------------------
c
c additional small correction for horizontal bias gradient
c (when I first measured it, I used the virtual overscan,
c but this includes some component of dark current).  I
c measured the correction using the lowest 100 pixels of
c the biases
c
      print*,'    CORRECT HORIZONTAL BIAS GRADIENT (SUPP)'
      call pixz_fix(pixz_raz) ! an additional bias-shift fix
      print*,'     '

      do i = 0001, 8412
      do j = 0001, 2070
         if (pixz_raz(i,j).lt.-500) pixz_raz(i,j) = 0.00
         enddo
         enddo
 
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_raz2rsz2.f"
c****                                         
c*********************************************
                                              
 
 
c--------------------------------------------------------------------
c
c This routine finds the smoothest possible image that is consistent
c with being the observed image plus readnoise.  This is necessary
c because we want the CTE-correction algorithm to produce smoothest
c possible reconstruction, consistent with the original image and the
c known readnoise.  This algorithm constructs a model that is smooth
c where the pixel-to-pixel variations can be thought of as being related
c to readnoide, but if the variations are too large, then it respects
c the pixel values.  Basically... it uses a 2-sigma threshold.
c
c This is strategy #1 in a two-pronged strategy to mitigate the readnoise
c amplification.  Strategy #2 will be to not iterate when the deblurring
c is less than the readnoise.
c
      subroutine sub_wfc3uv_raz2rsz(pixz_obs,pixz_mod,pixz_noi,RNSIG)
      implicit none
 
      real pixz_obs(8412,2070)
      real pixz_mod(8412,2070)
      real pixz_noi(8412,2070)
      real RNSIG
 
      integer i, j, jj
      real    pixz_adj(8412,2070)
      real    find_dadj
 
      real pval
      real dmin, d
      real pmin, p
      integer NIT
      real*8  rms
      integer nrms

      integer IMINU, IMAXU
      integer JMINU, JMAXU
      integer ISHO
      integer JSHO1, JSHO2
 
      print*,'                                                         '
      print*,'    ENTER wfc3uv_raz2rsz... RNSIG: ',RNSIG
      print*,'                                                         '
      print*,'          GOAL:  Remove the pixel-to-pixel variation     '
      print*,'                 that is most consistent with readnoise  '
      print*,'                 until the above sigma has been removed. '
      print*,'                 Iterate up to 99 times, removing at most'
      print*,'                 0.33 SIGMA each iteration from each     '
      print*,'                 (usually less).  Below, I just show some'
      print*,'                 pixels from the pre-scan region         '
      print*,'                 (20,1996:2004) that *should* be just    '
      print*,'                 readnoise.                              '
      print*,'                                                         '

c     call writfits_r4('pixz_obs.fits',pixz_obs,8412,2070)

      IMINU = 8412
      IMAXU = 0001
      JMINU = 2070
      JMAXU = 0001
 
      do i = 0001, 8412
      do j = 0001, 2070
         if (abs(pixz_obs(i,j)).gt.0.1) then
            if (i.lt.IMINU) IMINU = i
            if (i.gt.IMAXU) IMAXU = i
            if (j.lt.JMINU) JMINU = j
            if (j.gt.JMAXU) JMAXU = j
            endif
         if (.not.(pixz_obs(i,j).gt.-99999.)) then
            print*,'CORRUPTION! '
            print*,'   i: ',i
            print*,'   j: ',j
            print*,'   p: ',pixz_obs(i,j)
            stop
            endif
         pixz_mod(i,j) = pixz_obs(i,j)
         pixz_noi(i,j) = 0.
         pixz_adj(i,j) = 0.
         enddo
         enddo

      ISHO  = IMINU+20
      JSHO1 = JMAXU-25-4
      JSHO2 = JMAXU-25+4
 
      if (RNSIG.lt.0.1) return ! no readnoise mitigation needed

      print*,'              '
      print*,'IMINU/IMAXU : ',IMINU,IMAXU 
      print*,'JMINU/JMAXU : ',JMINU,JMAXU 
      print*,'       ISHO : ',ISHO
      print*,'JSHO1/JSHO2 : ',JSHO1,JSHO2
      print*,'              '
 
c-----------------------------------------------------------
c
c Go through the entire image and adjust pixels to make them
c smoother, but not so much that it is not consistent with
c readnoise.  Do this in baby steps so that each iteration
c does very little adjustment and information can get propagated
c down the line.
c
      write(*,*)
      write(*,109) ' ORIG ',' DIFF ','  NEW '
      write(*,108) (jj,jj=JSHO1,JSHO2),
     .             (jj,jj=JSHO1,JSHO2),
     .             (jj,jj=JSHO1,JSHO2)
  108 format(5x,' NIT',1x,'chgd RMS',
     .                    ' NPIXUSED ',
     .                    ' ICOL',
     .               3(5x,'J=',i4.4,8(i6.4)))
  109 format(5x,'    ',1x,'        ',
     .                    '          ',
     .                    '     ',
     .               3(5x,24x,a6,24x))
      rms = 0.
      nrms = 0.
      do NIT = 01, 75
c        do i = 0001, 8412
c        do j = 0001, 2070
         do i = IMINU, IMAXU
         do j = JMINU, JMAXU
            pval = pixz_mod(i,j)
            pixz_adj(i,j) = 0.0
            d = find_dadj(i,j,pixz_obs,pixz_mod,RNSIG)
            pixz_adj(i,j) = d
            if (j.eq.JSHO1.and.i.eq.ISHO)
     .      write(*,119) NIT,rms,nrms,i,
     .             (min(pixz_obs(i,jj),999.9),jj=JSHO1,JSHO2),
     .             (min(pixz_obs(i,jj)
     .                 -pixz_mod(i,jj),999.9),jj=JSHO1,JSHO2),
     .             (min(pixz_mod(i,jj),999.9),jj=JSHO1,JSHO2)
  119       format(5x,i4,1x,f8.4,1x,i8,1x,i5.4,3(5x,9f6.1))
            enddo
            enddo
c        do i = 0001, 8412
c        do j = 0001, 2070
         do i = IMINU, IMAXU
         do j = JMINU, JMAXU
            pixz_mod(i,j) = pixz_mod(i,j) + pixz_adj(i,j)*0.75
            pixz_noi(i,j) = pixz_obs(i,j) - pixz_mod(i,j)
            enddo
            enddo
         nrms = 0.
         rms  = 0.
         do i = 0001, 8412
         do j = 0001, 2070
            if (abs(pixz_obs(i,j)).gt.0.5) then
                rms  = rms  + (pixz_obs(i,j)-pixz_mod(i,j))**2
                nrms = nrms + 1
                endif
            enddo
            enddo
         rms = sqrt(rms/nrms)
         if (rms.gt.RNSIG) goto 1
         enddo!NIT
    1 continue
      print*,' '
 
      return
      end
 
 
 
 
 
 
 
 
 
c--------------------------------------------------------
c
c This subroutine determines for a given pixel how it can
c adjust in a way that is not inconsistent with its being
c readnoise.  To do this, it looks at its upper and lower
c neihbors and sees whether it is consistent with either
c (modulo readnoise).  To the extent that it is consistent
c then move it towards them.  But also bear in mind that
c that we don't want it to be more than 2 RN sigmas away
c from its original value.  This is pretty much a tug of
c war... with readnoise considerations pushing pixels to
c be closer to their neighbors, but the original pixel
c values also pull to keep the pixel where it was.  Some
c accommodation is made for both considerations.
c
      real function find_dadj(i,j,pixz_obs,pixz_mod,RNSIG)
      implicit none
 
      integer i,j
      real    pixz_obs(8412,2070)
      real    pixz_mod(8412,2070)
      real    RNSIG
 
      real    mval
      real    f1, f2
 
      real    dval0, dval0u, w0
      real    dval9, dval9u, w9
      real    dmod1, dmod1u, w1
      real    dmod2, dmod2u, w2
 
      mval = pixz_mod(i,j)
 
      dval0  = pixz_obs(i,j) - mval
      dval0u = dval0
      if (dval0u.gt. 1.00) dval0u =  1.00
      if (dval0u.lt.-1.00) dval0u = -1.00
 
      dval9 = 0.0
      if (i.gt.0001.and.i.lt.8412.and.
     .    j.gt.0001.and.j.lt.2070) then
          dval9 = ((pixz_obs(i  ,j+1) - pixz_mod(i  ,j+1))
     .            +(pixz_obs(i  ,j  ) - pixz_mod(i  ,j  ))
     .            +(pixz_obs(i  ,j+1) - pixz_mod(i  ,j+1))
     .            +(pixz_obs(i-1,j+1) - pixz_mod(i-1,j+1))
     .            +(pixz_obs(i-1,j  ) - pixz_mod(i-1,j  ))
     .            +(pixz_obs(i-1,j+1) - pixz_mod(i-1,j+1))
     .            +(pixz_obs(i+1,j+1) - pixz_mod(i+1,j+1))
     .            +(pixz_obs(i+1,j  ) - pixz_mod(i+1,j  ))
     .            +(pixz_obs(i+1,j+1) - pixz_mod(i+1,j+1)))/9.0
          endif
      dval9u = dval9u
      if (dval9u.gt. RNSIG*0.33) dval9u =  RNSIG*0.33
      if (dval9u.lt.-RNSIG*0.33) dval9u = -RNSIG*0.33
 
      dmod1 = 0.
      if (j.ge.0002) dmod1 = pixz_mod(i,j-1) - mval
      dmod1u = dmod1
      if (dmod1u.gt. RNSIG*0.33) dmod1u =  RNSIG*0.33
      if (dmod1u.lt.-RNSIG*0.33) dmod1u = -RNSIG*0.33
 
      dmod2 = 0.
      if (j.le.2069) dmod2 = pixz_mod(i,j+1) - mval
      dmod2u = dmod2
      if (dmod2u.gt. RNSIG*0.33) dmod2u =  RNSIG*0.33
      if (dmod2u.lt.-RNSIG*0.33) dmod2u = -RNSIG*0.33
 
 
 
c-------------------------------------------------
c
c if it's within 2 sigma of the readnoise, then
c tend to treat as readnoise; if it's farther off
c than that, then downweight the influence
c
      w0 =   dval0**2/(dval0**2+04*RNSIG**2)
      w9 =   dval9**2/(dval9**2+18*RNSIG**2)
      w1 = 4*RNSIG**2/(dmod1**2+04*RNSIG**2)
      w2 = 4*RNSIG**2/(dmod2**2+04*RNSIG**2)
 
      find_dadj = dval0u*w0*0.25 ! desire to keep the original pixel value
     .          + dval9u*w9*0.25 ! desire to keep the original sum over 3x3
     .          + dmod1u*w1*0.25 ! desire to get closer to the pixel below
     .          + dmod2u*w2*0.25 ! desire to get closer to the pixel above
                                 ! (note that with the last two, if a pixel
                                 !  is too discordant with its upper or lower
                                 !  that neighbor has less of an ability to
                                 !  pull it)
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/barsig.f"
c****                                         
c*********************************************
                                              
 
      subroutine barsig(xlist,NTOT,bar,sig,NUSE)
      implicit none
 
      integer NTOT
      real*4 xlist(NTOT)
      real*4 bar
      real*4 sig
      integer NUSE
 
      integer n
      real*8    bsum, ssum
      integer nsum
      integer NIT
 
 
      bar = 0.e0
      sig = 9e9
      do NIT = 1, 30
         bsum = 0.
         ssum = 0.
         nsum = 0.
         do n = 1, NTOT
            if (abs(xlist(n)-bar).le.2.50*sig) then
               bsum = bsum + xlist(n)
               ssum = ssum + (xlist(n)-bar)**2
               nsum = nsum + 1
               endif
            enddo
         if (nsum.gt.0) bar = bsum / nsum
         if (nsum.gt.1) sig = sqrt(ssum/(nsum-1))
         enddo
      NUSE = nsum
      if (nsum.le.1) sig = 0.999
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/bs_ik.f"
c****                                         
c*********************************************
                                              
 
 
c---------------------------------------------------------------
c
c This is an empirical correction for the horizontal bias
c gradient in WFC3/UVIS.  This is electronic and does *not*
c correspond to real electrons, so it should be removed before
c the correction is done.  This could be related to a hysteresis
c in the amplifier, similar to ACS's bias-shift effect.  Or
c it could be something completely different.  I don't know,
c but it really doesn't matter...
c
c The funtion takes in the column number (i) and the amplifier (k)
c and returns the adjustment to make for each pixel in that column
c
      real function bs_ik(i,k)
      implicit none
 
      integer i, k
 
c-------------------------------------
c
c locations where the fix is specified
c
      real    ii_n(26)
      common /ii_n_/ii_n
      data    ii_n/ 0000,
     .              0025,
     .              0026,
     .              0043,
     .              0060,
     .              0100,
     .              0200,
     .              0300,
     .              0400,
     .              0500,
     .              0600,
     .              0700,
     .              0800,
     .              0900,
     .              1000,
     .              1100,
     .              1200,
     .              1300,
     .              1400,
     .              1500,
     .              1600,
     .              1700,
     .              1800,
     .              1900,
     .              2000,
     .              2106/
 
      real    bs_kn(4,26)
      common /bs_k_/bs_kn
      data    bs_kn/ 0.00,  0.00,  0.00,  0.00, ! 0000
     .               0.00,  0.00,  0.00,  0.00, ! 0025
     .               0.19,  0.64, -0.01,  0.17, ! 0026
     .               0.24,  1.14,  0.02,  0.05, ! 0043
     .               0.21,  1.39,  0.05,  0.04, ! 0060
     .               0.14,  1.54,  0.11,  0.01, ! 0100
     .               0.21,  1.69,  0.14,  0.07, ! 0200
     .               0.21,  1.74,  0.19,  0.02, ! 0300
     .               0.16,  1.69,  0.24, -0.01, ! 0400
     .               0.07,  1.54,  0.22, -0.11, ! 0500
     .              -0.01,  1.39,  0.19, -0.21, ! 0600
     .              -0.06,  1.29,  0.14, -0.26, ! 0700
     .              -0.08,  1.24,  0.14, -0.31, ! 0800
     .              -0.11,  1.19,  0.13, -0.31, ! 0900
     .              -0.13,  1.15,  0.12, -0.34, ! 1000
     .              -0.14,  1.15,  0.12, -0.34, ! 1100
     .              -0.14,  1.15,  0.12, -0.34, ! 1200
     .              -0.14,  1.15,  0.12, -0.36, ! 1300
     .              -0.14,  1.15,  0.12, -0.36, ! 1400
     .              -0.14,  1.15,  0.12, -0.36, ! 1500
     .              -0.14,  1.15,  0.12, -0.36, ! 1600
     .              -0.14,  1.15,  0.12, -0.36, ! 1700
     .              -0.14,  1.15,  0.12, -0.36, ! 1800
     .              -0.14,  1.15,  0.12, -0.36, ! 1900
     .              -0.14,  1.15,  0.12, -0.36, ! 2000
     .              -0.14,  1.15,  0.12, -0.36/ ! 2106
 
      integer n
      real    ff
 
      bs_ik = 0.0
      do n = 1, 25
         if (i.ge.ii_n(n  ).and.
     .       i.le.ii_n(n+1)) then
             ff = 1.0*(i        -ii_n(n))/
     .                (ii_n(n+1)-ii_n(n))
             bs_ik = bs_kn(k,n) + ff*(bs_kn(k,n+1)-bs_kn(k,n))
             return
             endif
         enddo
 
      print*,'bs_ik failure...'
      print*,'   i: ',i
      print*,'   k: ',k
      stop
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/pixz_fix.f"
c****                                         
c*********************************************
                                              
 
c--------------------------------------------------------
c
c this is an additional fix to the horiz bias gradient;
c the original function was measured on the vertical overscan
c not the pixels closest to the readout amp.
c
      subroutine pixz_fix(pix)
      implicit none
 
      real pix(8412,2070)
      integer i, j
      integer k
      integer ii
      real    ff, adj
 
      real adj_ik(5,4)
      data adj_ik/
     .      -0.125, -0.125, -0.025, -0.025, -0.025,
     .      -0.075, -0.075,  0.125,  0.150,  0.150,
     .       0.000,  0.000,  0.100,  0.100,  0.100,
     .      -0.050,  0.075,  0.175,  0.200,  0.250/
 
      do k = 1, 4
      do j = 0001, 2070
         do i = 0001, 2048
            ii = 1 + int((i-1)/512)
            ff = (i-(ii-1)*512)/512.00
            adj = adj_ik(ii,k) + ff*(adj_ik(ii+1,k)-adj_ik(ii,k))
            pix(i+(k-1)*2103+25,j) = pix(i+(k-1)*2103+25,j) - adj
            enddo
         enddo
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/imgadd_r4.f"
c****                                         
c*********************************************
                                              
 
c--------------------------------------------------
c
c add two images together, including a re-scaling
c
c c = a + b*SCL
c
      subroutine imgadd_r4(a,SCL,b,c,XDIM,YDIM)
      implicit none
 
      integer XDIM, YDIM
      real a(XDIM,YDIM)
      real SCL
      real b(XDIM,YDIM)
      real c(XDIM,YDIM)
 
      integer i,j
 
      do j = 0001, YDIM
      do i = 0001, XDIM
         c(i,j) = a(i,j) + SCL*b(i,j)
         enddo
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/imgsub_r4.f"
c****                                         
c*********************************************
                                              
 
      subroutine imgsub_r4(a,SCL,b,c,XDIM,YDIM)
      implicit none
 
      integer XDIM, YDIM
      real a(XDIM,YDIM)
      real SCL
      real b(XDIM,YDIM)
      real c(XDIM,YDIM)
 
      integer i,j
 
      do j = 0001, YDIM
      do i = 0001, XDIM
         c(i,j) = a(i,j) - SCL*b(i,j)
         enddo
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/cowritfits_raw.f"
c****                                         
c*********************************************
                                              
 
 
c-----------------------------------------------------
c
c this routine writes a new RAW-type file, but preserves
c the header of the original RAW-type file (adding some
c to the first page, tho)
c
c
      subroutine cowritfits_raw(FILEI,FILEO,pixz,
     .                          CTEMOD_HEADER)
      implicit none
 
      character*80 FILEI
      character*80 FILEO
      real pixz(8412,2070)
 
      character*80 CTEMOD_HEADER(72)
      integer      Hs
 
c
c-------------------------------------
c
 
      real pix1(4206,2070)
      real pix4(4206,2070)
 
      integer nimg
      integer naxes
      integer laxis(3)
 
      character*8  field
      character*20 stream
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k, kk
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffc,buffb)
 
      integer  ifirst,  i1,  i2
      integer iifirst, ii1, ii2, ii
 
      integer np1, np2, npt
      integer nextend
      integer NREAD
      real bscale, bzero
      integer bitpix
 
      real dtde_l(11)
      real chg_leak(4,17)
      integer timeArray(3)
      integer dateArray(3)
 
      integer di
 
      logical atend
      logical FREAD
 
      real rDAT
      character*12 DATESTR
      character*12 TIMESTR
      common /rDAT_/rDAT,DATESTR,TIMESTR
 
      integer NMOD
      common /MMOD_/NMOD
      character*11 HOW(4)
 
      integer NIT2DO
      common/NIT2DO_/NIT2DO
 
      integer j
 
      logical VERBOSE
      common /VERBOSE_/VERBOSE
 
      character*80 BLANK
 
      character*80 STRING_HEAD(360)
      character*20 APERTURE
      integer h
      character*4  CCDAMP
 
c
c--------------------------------------------------------
c
 
      call fitshead2string(FILEI,STRING_HEAD)
      APERTURE = 'NONE'
      CCDAMP   = 'NONE'
      do h = 001, 360
         if (STRING_HEAD(h)(01:10).eq.'APERTURE= ')
     .       read(STRING_HEAD(h)(11:30),*) APERTURE
         if (STRING_HEAD(h)(01:10).eq.'CCDAMP  = ')
     .       read(STRING_HEAD(h)(11:30),*) CCDAMP
         enddo
      if (CCDAMP.ne.'ABCD') then
          print*,'                                              '
          print*,'CANNOT PRODUCE RAC IMAGE FOR SUBARRAY IMAGE...'
          print*,'MOVING ON TO NEXT STEP...                     '
          print*,'                                              '
          return
          endif
 
      if (VERBOSE) print*,'COPY IMAGES INTO SINGLE CHIP...'
      do i = 0001, 2103
      do j = 0001, 2070
         pix1(i+0000,j+0000) = pixz(i+0*2103,j)
         pix1(4207-i,j+0000) = pixz(i+1*2103,j)
         enddo
         enddo
      do i = 0001, 2103
      do j = 0001, 2070
         pix4(i+0000,2071-j) = pixz(i+2*2103,j)
         pix4(4207-i,2071-j) = pixz(i+3*2103,j)
         enddo
         enddo
 
      BLANK = '                                        '
     .     // '                                        '
 
 
      if (VERBOSE) print*,'OPEN FILES...'
      open(10,file=FILEI,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      open(11,file=FILEO,status='unknown',
     .     err=901,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      call itime(timeArray)
      call idate(dateArray)
 
      bscale = 1.0
      bzero  = 0.0
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
 
      i  = 0
      ii = 0
      NREAD = 0
 100  continue
      i  = i  + 1
      ii = ii + 1
      if (VERBOSE)
     .write(*,'(''READ AGAIN!   i = '',i8.8,1x,i8.8,3x,i2)')
     .                          i,ii,NREAD
      read(10,rec=i,iostat=ios) buffc
      atend = .false.
      do k = 00, 35
         if (VERBOSE) write(*,'(i9.9,1x,i2,1x,a80)')
     .                         i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+11:k*80+31)
         if (NREAD.eq.1.or.NREAD.eq.4) then
            if (field.eq.'BITPIX  ') then
                write(buffc(k*80+01:k*80+80),
     .               '(''BITPIX  =                  -32 '')')
                if (VERBOSE) write(*,'(i9.9,1x,i2,1x,a80)')
     .                             i,k,buffc(k*80+1:k*80+80)
                endif
            if (field.eq.'BZERO   ') then
                write(buffc(k*80+01:k*80+80),
     .               '(''BZERO   =                    0 '')')
                if (VERBOSE) write(*,'(i9.9,1x,i2,1x,a80)')
     .                             i,k,buffc(k*80+1:k*80+80)
                endif
            if (field.eq.'BSCALE  ') then
                write(buffc(k*80+01:k*80+80),
     .               '(''BSCALE  =                  1.0 '')')
                if (VERBOSE) write(*,'(i9.9,1x,i2,1x,a80)')
     .                             i,k,buffc(k*80+1:k*80+80)
                endif
            endif
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (field.eq.'DATAMIN ') buffc(01+k*80:80+k*80) = BLANK
         if (field.eq.'DATAMAX ') buffc(01+k*80:80+k*80) = BLANK
         if (buffc(k*80+01:k*80+3).eq.'END') then
            atend = .true.
            if (NREAD.eq.0) buffc(k*80+01:k*80+03) = '   '
            endif
         enddo
      if (VERBOSE) print*,'ATEND? ',atend
      if (.not.atend) then
         write(11,rec=ii,iostat=ios) buffc
         goto 100
         endif
      write(11,rec=ii,iostat=ios) buffc
 
      if (NREAD.eq.0) then
         ii = ii + 1
         do k = 00, 35
            buffc(k*80+01:k*80+80) = CTEMOD_HEADER(k+01+00)
            enddo
         write(11,rec=ii,iostat=ios) buffc
         ii = ii + 1
         do k = 00, 35
            buffc(k*80+01:k*80+80) = CTEMOD_HEADER(k+01+36)
            enddo
         write(11,rec=ii,iostat=ios) buffc
         endif
 
 
      if (VERBOSE) print*,'PROCESS... NREAD: ',NREAD



c
c new code from 2014.09.23:  write out all the extra
c     extensions
c
      if (NREAD.eq.6) then
  800    continue
         i  = i  + 1
         read(10,rec=i,iostat=ios) buffc
         if (ios.eq.0) then
            ii = ii + 1
            print*,'add: i=',i,' ----- ii=',ii
            write(11,rec=ii,iostat=ios) buffc
            goto 800
            endif
         close(10)
         close(11)
         return
         endif

c
c old code from before 2014.09.23
c 
c      if (NREAD.eq.6) then
c         close(10)
c         close(11)
c         return
c         endif
c
 
      if (NREAD.eq.1.or.NREAD.eq.4) then
         if (laxis(1).ne.4206.or.laxis(2).ne.2070)
     .       stop 'this routine can only write full-frame raw...'
         ifirst  = i + 1
         nbper   = 2*laxis(1)*laxis(2)
         npt     = laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         i1 = i+1 + nbyte1/2880
         i2 = i+1 + nbyte2/2880
         i  = i2
 
         iifirst = ii+1
         nbper   = 4*laxis(1)*laxis(2)
         npt     = laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         ii1 = ii+1 + nbyte1/2880
         ii2 = ii+1 + nbyte2/2880
 
         do ii = ii1, ii2, 1
            nbyte0 = (ii-iifirst)*2880+   1
            nbyteE = (ii-iifirst)*2880+2880
            np1 = (nbyte0-nbyte1)/4 + 1
            np2 = (nbyteE-nbyte1)/4 + 1
            if (NREAD.eq.1) call pix2buff_r4ee(buffb,pix1,np1,npt)
            if (NREAD.eq.4) call pix2buff_r4ee(buffb,pix4,np1,npt)
            write(11,rec=ii,iostat=ios) buffc
            enddo
         ii = ii2
         endif
 
      if (VERBOSE) print*,'  NREAD: ',NREAD
      NREAD = NREAD + 1
      if (VERBOSE) print*,'  i ---> ',i
      if (VERBOSE) print*,' ii ---> ',ii
      if (VERBOSE) print*,'  NREAD: ',NREAD
      goto  100
 
 
 
 900  continue
      print*,'cowritefits_flt: READFITS ERROR'
      print*,'           FILE: ',FILEI
      stop
 
 901  continue
      print*,'cowritefits_flt: OPEN FITS ERROR'
      print*,'           FILE: ',FILEO
      stop
 
      end
 
 
 
c-------------------------------------------------------
c
c
      subroutine pix2buff_r4ee(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real*4 pix(*)
      integer n1,nt
 
      byte b(4)
      real*4 r
      equivalence(r,b)
 
      integer i, npu, nbu
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (npu.ge.1.and.npu.le.nt) r = pix(npu)
         if (.not.LINUX_FLAG) then
            buff(nbu+1) = b(1)
            buff(nbu+2) = b(2)
            buff(nbu+3) = b(3)
            buff(nbu+4) = b(4)
            endif
         if (LINUX_FLAG) then
            buff(nbu+1) = b(4)
            buff(nbu+2) = b(3)
            buff(nbu+3) = b(2)
            buff(nbu+4) = b(1)
            endif
         enddo
 
      return
      end
 
c#include "../ROUTINES/cowritfits_flt.f"
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_cowrite_flt.f"
c****                                         
c*********************************************
                                              
 
c-----------------------------------------------------
c
c this routine will output an flt image, but will
c replace the pixels in the science extensions [1,4];
c it will *not* adjust the error array or the DQ
c array ; it keeps the original header but adds a
c couple extra pages to describe the CTE model
c
      subroutine cowritfits_flt(FILE_FLT,FILE_FLC,pixz_flc,
     .                          CTEMOD_HEADER)
      implicit none
 
      character*80 FILE_FLT
      character*80 FILE_FLC
      real pixz_flc(8412,2070)
 
      character*80 CTEMOD_HEADER(72)
 
c
c-------------------------------------
c
 
      real*4 pixc1(4096,2051)
      real*4 pixc4(4096,2051)
      real*4 pixa(2047,2050)
      real*4 pixx(1025,1024)
      real*4 pixy(0513,0512)
 
      integer nimg
      integer naxes
      integer laxis(3)
 
      character*8  field
      character*20 stream
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k, kk
      integer ik, jk
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffc,buffb)
 
      integer  ifirst,  i1,  i2
      integer iifirst, ii1, ii2, ii
 
      integer np1, np2, npt
      integer nextend
      integer NREAD
      real bscale, bzero
      integer bitpix
 
      real dtde_l(11)
      real chg_leak(4,17)
      integer timeArray(3)
      integer dateArray(3)
 
      integer di
 
      logical atend
      logical FREAD
 
      real rDAT
      character*12 DATESTR
      character*12 TIMESTR
      common /rDAT_/rDAT,DATESTR,TIMESTR
 
      real CTE_FRAC
      common /CTE_FRAC_/CTE_FRAC
 
      integer NMOD
      common /MMOD_/NMOD
      character*11 HOW(4)
 
      integer NIT2DO
      common/NIT2DO_/NIT2DO
 
      integer j, h
      integer NAPu
 
      logical VERBOSE
      common /VERBOSE_/VERBOSE
 
      character*80 STRING_HEAD(360)
      character*20 APERTURE
      character*4  CCDAMP
c
c--------------------------------------------------------
c
 
 
      print*,' '
      print*,'     ENTER sub_wfc3uv_cowrite_flt... FLT: ',FILE_FLT(1:40)
      print*,'                                 ... FLC: ',FILE_FLC(1:40)
      print*,' '
      print*,' pixz_flc(1049+0*2103,1024): ',pixz_flc(1049+0*2103,1024)
      print*,' pixz_flc(1049+1*2103,1024): ',pixz_flc(1049+1*2103,1024)
      print*,' pixz_flc(1049+2*2103,1024): ',pixz_flc(1049+2*2103,1024)
      print*,' pixz_flc(1049+3*2103,1024): ',pixz_flc(1049+3*2103,1024)
      print*,' '


      call fitshead2string(FILE_FLT,STRING_HEAD)
      APERTURE = 'NONE'
      CCDAMP   = 'NONE'
      do h = 001, 360
         if (STRING_HEAD(h)(01:10).eq.'APERTURE= ')
     .       read(STRING_HEAD(h)(11:30),*) APERTURE
         if (STRING_HEAD(h)(01:10).eq.'CCDAMP  = ')
     .       read(STRING_HEAD(h)(11:30),*) CCDAMP
        !write(*,'(i3.3,10x,a80,10x,a20)') h,STRING_HEAD(h),APERTURE
         enddo
      print*,'          APERTURE       : ',APERTURE
      print*,'          APERTURE(01:01): ',APERTURE(01:01)
      print*,'          APERTURE(02:12): ',APERTURE(02:12)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      print*,'          APERTURE(01:12): ',APERTURE(01:12)
      print*,'          APERTURE(01:15): ',APERTURE(01:15)
 
      NAPu = 0

      if (APERTURE(01:06).eq.'UVIS  '.or.
     .    APERTURE(01:06).eq.'UVIS1 '.or.
     .    APERTURE(01:06).eq.'UVIS2 '.or.
     .    APERTURE(01:09).eq.'UVIS-FIX '.or.
     .    APERTURE(01:09).eq.'UVIS1-FIX'.or.
     .    APERTURE(01:09).eq.'UVIS2-FIX'.or.
     .    APERTURE(01:09).eq.'G280-REF '.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD'.or.
     .    APERTURE(01:11).eq.'UVIS-CENTER'.or.
     .    APERTURE(01:11).eq.'UVIS-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS1-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS2-IR-FIX'.or.
     .    APERTURE(01:13).eq.'UVIS-QUAD-FIX') then
          print*,'          readfits_flt2pixz[1]: ',FILE_FLT(1:20)
          NAPu = 1
          do i = 0001, 2048
          do j = 0001, 2051
             pixc1(i+0000,j+0000) = pixz_flc(i+0*2103+25,j)
             pixc1(4097-i,j+0000) = pixz_flc(i+1*2103+25,j)
             enddo
             enddo
          print*,'          readfits_flt2pixz[4]: ',FILE_FLT(1:20)
          do i = 0001, 2048
          do j = 0001, 2051
             pixc4(i+0000,j+0000) = pixz_flc(i+2*2103+25,2052-j)
             pixc4(4097-i,j+0000) = pixz_flc(i+3*2103+25,2052-j)
             enddo
             enddo
          endif



 
      if (APERTURE(01:13).eq.'UVIS1-2K4-SUB') then
          NAPu = 2
          do i = 0001, 2048
          do j = 0001, 2050
             pixc4(i,j) = pixz_flc(0025+i+2*2103,2052-j)
             enddo
             enddo
          do i = 2049, 4096
          do j = 0001, 2050
             pixc4(i,j) = pixz_flc(025+(4097-i)+3*2103,2052-j)
             enddo
             enddo
          endif
 
      if (CCDAMP.eq.'A   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2A-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          NAPu = 3
          do j = 0001, 2050
          do i = 0001, 2047
             pixa(i,j) = pixz_flc(25+i+2*2103,2052-j)
             enddo
             enddo
          endif
          endif
 
      if (CCDAMP.eq.'B   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2B-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          NAPu = 4
          do j = 0001, 2050
          do i = 0001, 2047
             pixa(i,j) = pixz_flc(25+2049-i-3+3*2103+2,2052-j)
             enddo
             enddo
          endif
          endif
 
      if (CCDAMP.eq.'C   ') then
      if (APERTURE(01:14).eq.'UVIS2-2K2C-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          NAPu = 5
          do j = 0001, 2050
          do i = 0001, 2047
             pixa(i,j) = pixz_flc(25+i-2+0*2103+2,j+1)
             enddo
             enddo
          endif
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C1K1C-SUB') then
          NAPu = 6
          do i = 0001, 1024
          do j = 0001, 1024
             pixx(i,j) = pixz_flc(25+i+0*2103,j+1)
             enddo
             enddo
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C512C-SUB') then
          NAPu = 7
          do i = 0001, 0513
          do j = 0001, 0512
             pixy(i,j) = pixz_flc(25+i+0*2103,j+1)
             enddo
             enddo
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C512D-SUB') then
          NAPu = 7
          do i = 0001, 0513
          do j = 0001, 0512
             pixy(514-i,j) = pixz_flc(25+i+1*2103,j+1)
             enddo
             enddo
          endif
 
      if (APERTURE(01:15).eq.'UVIS1-C512A-SUB') then
          NAPu = 7
          do i = 0001, 0513
          do j = 0001, 0512
             pixy(i,513-j) = pixz_flc(25+i+2*2103,j+1)
             enddo
             enddo
          endif
 
      if (APERTURE(01:15).eq.'UVIS1-C512B-SUB') then
          NAPu = 7
          do i = 0001, 0513
          do j = 0001, 0512
             pixy(514-i,513-j) = pixz_flc(25+i+3*2103,j+1)
             enddo
             enddo
          endif
 
      if (NAPu.eq.0)
     .    stop 'sub_wfc3uv_cowrit_flt:  NO APERTURE IDENTIFIED...'
 
 
 
      if (VERBOSE) print*,'OPEN FILES...'
      open(10,file=FILE_FLT,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      open(11,file=FILE_FLC,status='unknown',
     .     err=901,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      call itime(timeArray)
      call idate(dateArray)
 
      bscale = 1.0
      bzero  = 0.0
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
 
      i  = 0
      ii = 0
      NREAD = 0
 100  continue
      i  = i  + 1
      ii = ii + 1
      if (VERBOSE)
     .write(*,'(''READ AGAIN!   i = '',i8.8,1x,i8.8,3x,i2)')
     .                          i,ii,NREAD
      read(10,rec=i,iostat=ios) buffc
      atend = .false.
      do k = 00, 35
         if (VERBOSE) write(*,'(i9.9,1x,i2,1x,a80)')
     .                         i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+11:k*80+31)
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (buffc(k*80+01:k*80+3).eq.'END') then
            atend = .true.
            if (NREAD.eq.0) buffc(k*80+01:k*80+03) = '   '
            endif
         enddo
      if (VERBOSE) print*,'ATEND? ',atend
      if (.not.atend) then
         write(11,rec=ii,iostat=ios) buffc
         goto 100
         endif
      write(11,rec=ii,iostat=ios) buffc
 
      if (NREAD.eq.0) then
         ii = ii + 1
         do k = 00, 35
            buffc(k*80+01:k*80+80) = CTEMOD_HEADER(k+01+00)
            enddo
         write(11,rec=ii,iostat=ios) buffc
         ii = ii + 1
         do k = 00, 35
            buffc(k*80+01:k*80+80) = CTEMOD_HEADER(k+01+36)
            enddo
         write(11,rec=ii,iostat=ios) buffc
         endif
 

      print*,'NAPu: ',NAPu
 
      write(*,'(6x,''cowritfits_flt: '',a18,''['',i1,'']'')')
     .                                  FILE_FLT(01:18),NREAD
      if (VERBOSE) print*,'PROCESS... NREAD: ',NREAD
      if (VERBOSE) print*,'               i: ',i
      if (VERBOSE) print*,'              ii: ',ii
 
      if (NREAD.eq.1.or.NREAD.eq.4) then
         ifirst  = i + 1
         nbper   = 4*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         i1 = i+1 + nbyte1/2880
         i2 = i+1 + nbyte2/2880
         i  = i2
 
         iifirst = ii+1
         nbper   = 4*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         ii1 = ii+1 + nbyte1/2880
         ii2 = ii+1 + nbyte2/2880
 
         print*,'        '
         print*,' NREAD: ',NREAD
         print*,'    l1: ',laxis(1)
         print*,'    l2: ',laxis(2)
         print*,' nbper: ',nbper
         print*,'   ii1: ',ii1
         print*,'   ii2: ',ii2
         print*,'  NAPu: ',NAPu,pixy(1,1)
         print*,'        '
 
         do ii = ii1, ii2, 1
            nbyte0 = (ii-iifirst)*2880+   1
            nbyteE = (ii-iifirst)*2880+2880
            np1 = (nbyte0-nbyte1)/4 + 1
            np2 = (nbyteE-nbyte1)/4 + 1
            if (NAPu.eq.1.and.
     .          NREAD.eq.1) call pix2buff_r4eee(buffb,pixc1,np1,npt)
            if (NAPu.eq.1.and.
     .          NREAD.eq.4) call pix2buff_r4eee(buffb,pixc4,np1,npt)
            if (NAPu.eq.2)  call pix2buff_r4eee(buffb,pixc4,np1,npt)
            if (NAPu.eq.3)  call pix2buff_r4eee(buffb,pixa ,np1,npt)
            if (NAPu.eq.4)  call pix2buff_r4eee(buffb,pixa ,np1,npt)
            if (NAPu.eq.5)  call pix2buff_r4eee(buffb,pixa ,np1,npt)
            if (NAPu.eq.6)  call pix2buff_r4eee(buffb,pixx ,np1,npt)
            if (NAPu.eq.7)  call pix2buff_r4eee(buffb,pixy ,np1,npt)
            write(11,rec=ii,iostat=ios) buffc
            enddo
         ii = ii2
         endif
 
      if (NREAD.eq.2.or.NREAD.eq.5) then
         ifirst  = i + 1
         nbper   = 4*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         i1 = i+1 + nbyte1/2880
         i2 = i+1 + nbyte2/2880
         i  = i2
 
         iifirst = ii+1
         nbper   = 4*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         ii1 = ii+1 + nbyte1/2880
         ii2 = ii+1 + nbyte2/2880
 
         do ii = ii1, ii2, 1
            i = i1 + (ii-ii1)
            read( 10,rec= i,iostat=ios) buffc
            write(11,rec=ii,iostat=ios) buffc
            enddo
          i =  i2
         ii = ii2
         print*,' NREAD: ',NREAD,nbper,laxis(1),laxis(2)
         endif
 
      if (NREAD.eq.3.or.NREAD.eq.6) then
         ifirst  = i + 1
         nbper   = 2*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         i1 = i+1 + nbyte1/2880
         i2 = i+1 + nbyte2/2880
         i  = i2
 
         iifirst = ii+1
         nbper   = 2*laxis(1)*laxis(2)
         npt     =   laxis(1)*laxis(2)
         nbyte1  = 1
         nbyte2  = nbper
         ii1 = ii+1 + nbyte1/2880
         ii2 = ii+1 + nbyte2/2880
 
         do ii = ii1, ii2, 1
            i = i1 + (ii-ii1)
            read( 10,rec= i,iostat=ios) buffc
            write(11,rec=ii,iostat=ios) buffc
            enddo
          i =  i2
         ii = ii2
         print*,' NREAD: ',NREAD,nbper,laxis(1),laxis(2)
         endif
 
      if (NAPu.gt.1.and.NREAD.eq.3) then
  801    continue
         i  = i  + 1
         read(10,rec=i,iostat=ios) buffc
         if (ios.eq.0) then
            ii = ii + 1
            print*,'add: i=',i,' ----- ii=',ii
            write(11,rec=ii,iostat=ios) buffc
            goto 801
            endif
         close(10)
         close(11)
         return
         endif

 
      if (NREAD.eq.6) then
  800    continue
         i  = i  + 1
         read(10,rec=i,iostat=ios) buffc
         if (ios.eq.0) then
            ii = ii + 1
            print*,'add: i=',i,' ----- ii=',ii
            write(11,rec=ii,iostat=ios) buffc
            goto 800
            endif
         close(10)
         close(11)
         return
         endif


 
 
      if (VERBOSE) print*,'  NREAD: ',NREAD
      NREAD = NREAD + 1
      if (VERBOSE) print*,'  i ---> ',i
      if (VERBOSE) print*,' ii ---> ',ii
      if (VERBOSE) print*,'  NREAD: ',NREAD
 
      goto  100
 
 
 
 900  continue
      print*,'cowritefits_flt: READFITS ERROR'
      print*,'           FILE: ',FILE_FLT
      stop
 
 901  continue
      print*,'cowritefits_flt: OPEN FITS ERROR'
      print*,'           FILE: ',FILE_FLC
      stop
 
      end
 
 
 
c-------------------------------------------------------
c
c
      subroutine pix2buff_r4eee(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real*4 pix(*)
      integer n1,nt
 
      byte b(4)
      real*4 r
      equivalence(r,b)
 
      integer i, npu, nbu
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (npu.ge.1.and.npu.le.nt) r = pix(npu)
         if (.not.LINUX_FLAG) then
            buff(nbu+1) = b(1)
            buff(nbu+2) = b(2)
            buff(nbu+3) = b(3)
            buff(nbu+4) = b(4)
            endif
         if (LINUX_FLAG) then
            buff(nbu+1) = b(4)
            buff(nbu+2) = b(3)
            buff(nbu+3) = b(2)
            buff(nbu+4) = b(1)
            endif
         enddo
 
      return
      end
 
 
 
 
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/find_FF.f"
c****                                         
c*********************************************
                                              
 
c---------------------------------------------------------------------
c
c This routine takes a date string and determines the CTE scaling
c appropriate for tha tdate, given that WFC3/UVIS was installed on
c about May 11, 2009 and the model was constructed to be valid on
c aobut Sep  3, 2012, a little over three years after installation.
c
 
      real function find_FF(STRING_HEAD,DATE_STRING,rDATu,rDAT0,rDAT1)
      implicit none
 
      character*80 STRING_HEAD(360)
      character*12 DATE_STRING
      real         rDATu
      real         rDAT0
      real         rDAT1
 
      integer n
      integer iYEAR
      integer iMONTH
      integer iDAY
 
      integer DOY(12)
      common /DOY_/DOY
      data DOY / 000, 031, 059, 090, 120, 151,
     .           181, 212, 243, 273, 304, 334/
 
      DATE_STRING = 'NULL'
      do n = 1, 360
         if (STRING_HEAD(n)(1:8).eq.'DATE-OBS') then
            DATE_STRING = STRING_HEAD(n)(11:23)
            endif
         enddo
 
      if (DATE_STRING(1:4).eq.'NULL') stop 'NULL DATE STRING...'
 
      if (DATE_STRING(01:01).ne.'''') stop 'DATE_STRING WRONG FORMAT...'
      if (DATE_STRING(12:12).ne.'''') stop 'DATE_STRING WRONG FORMAT...'
 
      read(DATE_STRING(02:05),*) IYEAR
      read(DATE_STRING(07:08),*) IMONTH
      read(DATE_STRING(10:11),*) IDAY
 
      rDATu = iYEAR + (DOY(iMONTH)+iDAY)/365.25
      rDAT0 = 2009  + (DOY(5)     +  11)/365.25
      rDAT1 = 2012  + (DOY(9)     +   3)/365.25
 
      find_FF = (rDATu-rDAT0)/
     .          (rDAT1-rDAT0)
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/fill_hdr_page.f"
c****                                         
c*********************************************
                                              
 
c-----------------------------------------------------------------------
c
c This subroutine fills a couple pages of header with information about
c the CTE model used.
c
      subroutine fill_hdr_page(CTEMOD_HEADER,Hs,
     .                      q_w,dpde_w,tprof_w,rprof_wt,cprof_wt,Ws,
     .                      CTE_FF,DATE_STRING,rDATu,rDAT0,rDAT1,
     .                      FILE_RAW, FILE_RAC,
     .                      DO_CRPROTECT, RNMIT)
 
      implicit none
 
      character*80 CTEMOD_HEADER(72)
      integer      Hs
 
      integer        q_w(_WDIM_)     ! output: the run of charge with level #L
      real        dpde_w(_WDIM_)     ! output: the run of charge loss with level #L
      integer    tprof_w(_WDIM_)     ! output: the length of trail for charge level #L
      real      rprof_wt(_WDIM_,100) ! output: the emission probability as fn of downhill pixel
      real      cprof_wt(_WDIM_,100) ! output: the cumulative probability cprof_t( 0001 ) = 1.000-rprof_t(1)
      integer   Ws
 
      real         CTE_FF
      real         rDATu
      real         rDAT1, rDAT0
      character*12 DATE_STRING
      character*80 FILE_RAW
      character*80 FILE_RAC
      logical      DO_CRPROTECT
      real         RNMIT
      integer      H
c
c-----------------------------------------------------------------------------------------------------------
c
      integer q1c2_u(2,_UDIM_)
      common /q1c2_u_ /q1c2_u           ! cumulative traps
 
      real    chg_leak(5,16)
      common /chg_leak_/chg_leak
 
c
c-----------------------------------------------------------------------------------------------------------
c
      integer u, r, n, t
 
      do H = 1, 72
         write(CTEMOD_HEADER(H),'(80('' ''))')
         enddo
 
      Hs = 0
      write(CTEMOD_HEADER(01),'('' '')')
      write(CTEMOD_HEADER(02),'(''          / CTE BASIS MODEL'')')
      write(CTEMOD_HEADER(03),'(''          / PARAMETERS:    '')')
      write(CTEMOD_HEADER(04),'('' '')')
      write(CTEMOD_HEADER(05),'(''CTE_SOFT= '',a5,19x,55a)') ' v0.1 ',
     .                   '/ WFC3/UVIS CTE SOFTWARE VERSION/'
      write(CTEMOD_HEADER(06),'('' '')')
      write(CTEMOD_HEADER(07),'(''          '',5x,19x,55a)')
     .                   '/** THIS IS AN ALPHA RELEASE **/'
      write(CTEMOD_HEADER(08),'(''          '',5x,19x,55a)')
     .                   '/** WE RESERVE THE RIGHT TO  **/'
      write(CTEMOD_HEADER(09),'(''          '',5x,19x,55a)')
     .                   '/** MAKE MAJoR CHANGES       **/'
      write(CTEMOD_HEADER(10),'('' '')')
      write(CTEMOD_HEADER(11),'(''CTE_TDIM= '',i3,21x,55a)') _TDIM_,
     .                   '/ MAX LENGTH OF CTE TRAIL         /'
      write(CTEMOD_HEADER(12),'(''CTE_NPSS= '',i3,21x,55a)') _NITCTE_,
     .                   '/ NUMBER OF PASSES TO EVAL FWD MOD/'
      write(CTEMOD_HEADER(13),'(''CTE_NRST= '',i3,21x,55a)') _NITERN_,
     .                   '/ NUMBER OF ITERnS FOR REV RESTORn/'
      write(CTEMOD_HEADER(14),'('' '')')
      write(CTEMOD_HEADER(15),'(''          / TRAP DISTRIBUTION:   '')')
      write(CTEMOD_HEADER(16),'(''          / CHG LEV     CUM TRAPS'')')
      Hs = 17
      do U = 1, _UDIM_
         Hs = Hs + 1
         write(CTEMOD_HEADER(Hs),801) U,q1c2_u(1,U),q1c2_u(2,U)
  801    format('CTE_QC',i2.2,' = ',3x,i5,9x,i5)
         enddo
      write(CTEMOD_HEADER(Hs+1),'('' '')')
      write(CTEMOD_HEADER(Hs+2),'(''          / TRAIL PROFILE     '')')
      write(CTEMOD_HEADER(Hs+3),802)
  802 format('          / PIXEL   q=1    ',
     .                            '   q=10   ',
     .                            '   q=100  ',
     .                            '   q=1000 ',
     .                            '   q=10000')
      Hs = Hs + 3
      do n = 1, 16
         if (n.eq.01) t = 001
         if (n.eq.02) t = 002
         if (n.eq.03) t = 003
         if (n.eq.04) t = 005
         if (n.eq.05) t = 008
         if (n.eq.06) t = 012
         if (n.eq.07) t = 016
         if (n.eq.08) t = 020
         if (n.eq.09) t = 025
         if (n.eq.10) t = 030
         if (n.eq.11) t = 040
         if (n.eq.12) t = 050
         if (n.eq.13) t = 060
         if (n.eq.14) t = 070
         if (n.eq.15) t = 080
         if (n.eq.16) t = 090
         if (n.eq.17) t = 100
         Hs = Hs + 1
         write(CTEMOD_HEADER(Hs),810) n,t,(chg_leak(r,n),r=1,5)
  810    format('CTE_TR',i2.2,'=  ',i4.3,3x,5f10.6)
         enddo
      write(CTEMOD_HEADER(Hs+1),810) 17,100,(0.00,r=1,5)
      write(CTEMOD_HEADER(Hs+2),'('' '')')
      Hs = Hs + 2
      write(CTEMOD_HEADER(Hs+1),'(''CTE_DATE= '',a12,12x,40a)')
     .      DATE_STRING,  '/ DATE OF OBS                     /'
      write(CTEMOD_HEADER(Hs+2),'(''CTE_DATU= '',f12.6,12x,40a)')
     .      rDATu,        '/ DATE OF OBS (FRAC YRS)          /'
      write(CTEMOD_HEADER(Hs+3),'(''CTE_DAT0= '',f12.6,12x,40a)')
     .      rDAT0,        '/ DATE OF WFC3 INSTALL (FRAC YRS) /'
      write(CTEMOD_HEADER(Hs+4),'(''CTE_DAT1= '',f12.6,12x,40a)')
     .      rDAT1,        '/ DATE OF MODEL (FRAC YEARS)      /'
      write(CTEMOD_HEADER(Hs+5),'(''CTE_FRAC= '',f12.6,12x,40a)')
     .      CTE_FF,       '/ SCALING OF CTE MODEL            /'
      write(CTEMOD_HEADER(Hs+6),'('' '')')
      write(CTEMOD_HEADER(Hs+7),'(''FILE_RAW= '',a,a18,a,4x,40a)')
     .      '''',FILE_RAW(1:18),'''','/ RAW FILE INPUT /'
      write(CTEMOD_HEADER(Hs+8),'(''FILE_RAC= '',a,a18,a,4x,40a)')
     .      '''',FILE_RAC(1:18),'''','/ RAC FILE INPUT /'
      Hs = Hs + 8
      write(CTEMOD_HEADER(Hs+1),'(''DOCRPROT = '',l5,18x,40a)')
     .      DO_CRPROTECT,'/ STOP READOUT-CR OVER-SUB (DEF=T)/'
      write(CTEMOD_HEADER(Hs+2),'(''CTERNMIT = '',f12.6,11x,40a)')
     .      RNMIT,       '/ RN TO MITIGATE (DEF=3.25)       /'
      write(CTEMOD_HEADER(Hs+3),'(''END'')')
      Hs = Hs + 3
      if (Hs.gt.72) stop ' Hs.gt.72 '
 
      if (.false.) then
         do H = 1, 72
            write(*,'(i2.2,1x,80a)') H,CTEMOD_HEADER(H)
            enddo
         endif
 
      do H = 1, 72
         CTEMOD_HEADER(H) = 'HISTORY ' // CTEMOD_HEADER(H)(1:72)
         enddo
 
      if (.false.) then
         do H = 1, 72
            write(*,'(i2.2,1x,80a)') H,CTEMOD_HEADER(H)(1:80)
            enddo
         endif
 
      CTEMOD_HEADER(72) =
     .     'END                                     ' //
     .     '                                        '
 
      return
      end
 
 
c#include "../ROUTINES/readfits_flt2pixz.f"
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/sub_wfc3uv_read_flt.f"
c****                                         
c*********************************************
                                              
 
c--------------------------------------------------------
c
c This will read in an _flt.fits image into an array
c in pixz format
c
      subroutine sub_wfc3uv_read_flt(FILE_FLT,pixz_flt)
      implicit none
 
      character*80 FILE_FLT
      real*4       pixz_flt(8412,2070)
      real*4       pixc(4096,2051)
      real*4       pixa(2047,2050)
      real*4       pixx(1025,1024)
      real*4       pixy(0513,0512)
      integer      i,j
 
      integer      h
      character*80 STRING_HEAD(360)
      character*20 APERTURE
      character*04 CCDAMP
 
 
      print*,'     ENTER sub_wfc3uv_read_flt... ',FILE_FLT(1:50)
 
      do i = 0001, 8412
      do j = 0001, 2070
         pixz_flt(i,j) = 0.0
         enddo
         enddo
 
c     call query_hdr(FILE_FLT,'APERTURE',APERTURE)
c     print*,'           APERTURE: ',APERTURE
 
      call fitshead2string(FILE_FLT,STRING_HEAD)
      APERTURE = 'NONE'
      CCDAMP   = 'NONE'
      do h = 001, 360
         if (STRING_HEAD(h)(01:10).eq.'APERTURE= ')
     .       read(STRING_HEAD(h)(11:30),*) APERTURE
         if (STRING_HEAD(h)(01:10).eq.'CCDAMP  = ')
     .       read(STRING_HEAD(h)(11:30),*) CCDAMP
        !write(*,'(i3.3,10x,a80,10x,a20)') h,STRING_HEAD(h),APERTURE
         enddo
      print*,'          APERTURE       : ',APERTURE
      print*,'          APERTURE(01:01): ',APERTURE(01:01)
      print*,'          APERTURE(02:12): ',APERTURE(02:12)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      if (APERTURE(01:01).eq.' ') APERTURE = APERTURE(02:20)
      print*,'          APERTURE(01:12): ',APERTURE(01:12)
      print*,'          APERTURE(01:15): ',APERTURE(01:15)
 
      if (APERTURE(01:06).eq.'UVIS  '.or.
     .    APERTURE(01:06).eq.'UVIS1 '.or.
     .    APERTURE(01:06).eq.'UVIS2 '.or.
     .    APERTURE(01:09).eq.'UVIS-FIX '.or.
     .    APERTURE(01:09).eq.'UVIS1-FIX'.or.
     .    APERTURE(01:09).eq.'UVIS2-FIX'.or.
     .    APERTURE(01:09).eq.'G280-REF '.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD'.or.
     .    APERTURE(01:11).eq.'UVIS-CENTER'.or.
     .    APERTURE(01:11).eq.'UVIS-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS1-IR-FIX'.or.
     .    APERTURE(01:12).eq.'UVIS2-IR-FIX'.or.
     .    APERTURE(01:13).eq.'UVIS-QUAD-FIX') then
          print*,'          readfits_flt2pixz[1]: ',FILE_FLT(1:20)
          call readfits_r4e(FILE_FLT,pixc,4096,2051,1)
          do i = 0001, 2048
          do j = 0001, 2051
             pixz_flt(i+0*2103+25,j) = pixc(i+0000,j+0000)
             pixz_flt(i+1*2103+25,j) = pixc(4097-i,j+0000)
             enddo
             enddo
          print*,'          readfits_flt2pixz[4]: ',FILE_FLT(1:20)
          call readfits_r4e(FILE_FLT,pixc,4096,2051,4)
          do i = 0001, 2048
          do j = 0001, 2051
             pixz_flt(i+2*2103+25,2052-j) = pixc(i+0000,j+0000)
             pixz_flt(i+3*2103+25,2052-j) = pixc(4097-i,j+0000)
             enddo
             enddo
          return
          endif
 
      if (APERTURE(01:13).eq.'UVIS1-2K4-SUB') then
          call readfits_r4e(FILE_FLT,pixc,4096,2050,1)
          do i = 0001, 2048
          do j = 0001, 2050
             pixz_flt(0025+i+2*2103,2052-j) = pixc(i,j)
             enddo
             enddo
          do i = 2049, 4096
          do j = 0001, 2050
             pixz_flt(025+(4097-i)+3*2103,2052-j) = pixc(i,j)
             enddo
             enddo
          return
          endif
 
      if (CCDAMP.eq.'A   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2A-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_r4e(FILE_FLT,pixa,2047,2050,1)
          do j = 0001, 2050
          do i = 0001, 2047
             pixz_flt(25+i+2*2103,2052-j) = pixa(i,j)
             enddo
             enddo
          return
          endif
          endif
 
      if (CCDAMP.eq.'B   ') then
      if (APERTURE(01:14).eq.'UVIS1-2K2B-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_r4e(FILE_FLT,pixa,2047,2050,1)
          do j = 0001, 2050
          do i = 0001, 2047
             pixz_flt(25+2049-i-3+3*2103+2,2052-j) = pixa(i,j)
             enddo
             enddo
          return
          endif
          endif
 
      if (CCDAMP.eq.'C   ') then
      if (APERTURE(01:14).eq.'UVIS2-2K2C-SUB'.or.
     .    APERTURE(01:09).eq.'UVIS-QUAD') then
          call readfits_r4e(FILE_FLT,pixa,2047,2050,1)
          do j = 0001, 2050
          do i = 0001, 2047
             pixz_flt(25+i-2+0*2103+2,j+1) = pixa(i,j)
             enddo
             enddo
          return
          endif
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C1K1C-SUB') then
          call readfits_r4e(FILE_FLT,pixx,1025,1024,1)
          do i = 0001, 1024
          do j = 0001, 1024
             pixz_flt(25+i+0*2103,j+1) = pixx(i,j)
             enddo
             enddo
          return
          endif

      if (APERTURE(01:15).eq.'UVIS2-C512C-SUB') then
          call readfits_r4e(FILE_FLT,pixy,513,512,1)
          do i = 0001, 0513
          do j = 0001, 0512
             pixz_flt(25+i+0*2103,j+1) = pixy(i,j)
             enddo
             enddo
          return
          endif
 
      if (APERTURE(01:15).eq.'UVIS2-C512D-SUB') then
          call readfits_r4e(FILE_FLT,pixy,513,512,1)
          do i = 0001, 0513
          do j = 0001, 0512
             pixz_flt(25+i+1*2103,j+1) = pixy(514-i,j)
             enddo
             enddo
          return
          endif
 
      if (APERTURE(01:15).eq.'UVIS1-C512A-SUB') then
          call readfits_r4e(FILE_FLT,pixy,513,512,1)
          do i = 0001, 0513
          do j = 0001, 0512
             pixz_flt(25+i+2*2103,j+1) = pixy(i,513-j)
             enddo
             enddo
          return
          endif
 
      if (APERTURE(01:15).eq.'UVIS1-C512B-SUB') then
          call readfits_r4e(FILE_FLT,pixy,513,512,1)
          do i = 0001, 0513
          do j = 0001, 0512
             pixz_flt(25+i+3*2103,j+1) = pixy(514-i,513-j)
             enddo
             enddo
          return
          endif
 
      print*,'sub_wfc3uv_read_flt() not ready for aperture = ',APERTURE
      stop
      end


 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/convert_r2z.f"
c****                                         
c*********************************************
                                              
 
c---------------------------------------------------
c
c As its name suggests, this routine takes an image
c in jay's 4096x4096 vertically abutted format and
c generates an image in "z" format, 8412x2070 ; it
c puts zeros into the prescans/overscans as well as
c into the image pixels that fall outside of the
c 4096x4096 boundary (a few useless rows)
c
c
      subroutine convert_r2z(pixr,pixz)
      implicit none
 
      real pixr(4096,4096)
      real pixz(8412,2070)
 
      integer i,j
 
      do j = 0001, 2070
      do i = 0001, 8412
         pixz(i,j) = 0.00
         enddo
         enddo
 
      do i = 0001, 2048
      do j = 0001, 2048
         pixz(i+0*2103+25,j) = pixr(i+0000,j+0000)
         pixz(i+1*2103+25,j) = pixr(4097-i,j+0000)
         if (j.ge.4) then
            pixz(i+2*2103+25,j) = pixr(i+0000,4097-j+0003)
            pixz(i+3*2103+25,j) = pixr(4097-i,4097-j+0003)
            endif
         enddo
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/convert_z2r.f"
c****                                         
c*********************************************
                                              
 
c-------------------------------------------------
c
c takes an image in "z" format, which is 8412x2070
c horizonally abutted, and converts it into "r" format,
c which is 4096x4096 vertically abutted
c
 
      subroutine convert_z2r(pixz,pixr)
      implicit none
 
      real pixz(8412,2070)
      real pixr(4096,4096)
 
      integer i,j
 
      do i = 0001, 2048
      do j = 0001, 2048
         pixr(i+0000,j+0000) = pixz(i+0*2103+25,j)
         pixr(4097-i,j+0000) = pixz(i+1*2103+25,j)
         pixr(i+0000,4097-j) = pixz(i+2*2103+25,j+003)
         pixr(4097-i,4097-j) = pixz(i+3*2103+25,j+003)
         enddo
         enddo
 
      do i = 0001, 4096
         pixr(i,2046) = -750
         pixr(i,2047) = -750
         pixr(i,2048) = -750
         pixr(i,2049) = -750
         pixr(i,2050) = -750
         pixr(i,2051) = -750
         enddo
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/readfits_i2e.f"
c****                                         
c*********************************************
                                              
 
c----------------------------------------------------------
c
c read in an i2 image with extensions
c
 
      subroutine readfits_i2e(FILEI,pix,NDIMX,NDIMY,NEXTENU)
      implicit none
 
      character*80 FILEI
      integer   NDIMX,NDIMY
      integer   NEXTENU
      integer*2 pix(NDIMX,NDIMY)
 
      character*80 FILEU
      character*70 INFO(10)
      common / fitsinfo / INFO
 
      integer naxes
      integer laxis(3)
      integer NXF
      integer NYF
 
      character*8  field
      character*40 stream
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k
      integer j
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffc,buffb)
 
      integer ifirst, i1, i2
 
      integer np1, np2, npt
      integer nextend
      integer nread
      real bscale, bzero
      integer bitpix
 
      character*70 HDR(25)
      common/HDR/HDR
 
      logical DIAG
      data DIAG /.false./
      integer NEND
      integer ii
 
      FILEU = FILEI
      do i = 75,2,-1
         if (FILEI(i:i+4).eq.'.fits') then
            FILEU = FILEI(1:i+4)
            do ii = i+5, 80
               FILEU(ii:ii) = ' '
               enddo
            endif
         enddo
 
      if (DIAG) then
         print*,'enter readfits_i2e...'
         write(*,'(''FILEI: '',80a)') FILEI
         write(*,'(''FILEU: '',80a)') FILEU
         endif
 
      open(10,file=FILEU,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      if (DIAG) print*,'...opened'
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
      do i = 1, 10
         INFO(i) = ' '
         enddo
 
      BSCALE = 1.0
      BZERO  = 0.0
 
      NEXTEND = 0
      NEND = -1
      i = 0
      nread = 0
 100  continue
      i = i + 1
      if (DIAG) print*,'READREC: ',i
      read(10,rec=i,iostat=ios) buffc
      do k = 0, 35, 1
         if (DIAG) write(*,'(i4,1x,i4,1x,a80)')
     .                   i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+11:k*80+51)
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (field.eq.'NAXIS3  ') read(stream,*) laxis(3)
         if (field.eq.'NEXTEND ') read(stream,*) nextend
         if (field.eq.'BITPIX  ') read(stream,*) bitpix
         if (field.eq.'BSCALE  ') read(stream,*) bscale
         if (field.eq.'BZERO   ') read(stream,*) bzero
 
         if (field.eq.'EXPTIME ') INFO(1) = stream
         if (field.eq.'FILTNAM1') INFO(2) = stream
         if (field.eq.'FILENAME') INFO(3) = stream
         if (field.eq.'DATE-OBS') INFO(4) = stream
         if (field.eq.'TIME-OBS') INFO(5) = stream
         if (field.eq.'DEC_TARG') INFO(6) = stream
         if (field.eq.'RA_TARG ') INFO(7) = stream
         if (field.eq.'DEC_DEG ') INFO(6) = stream
         if (field.eq.'RA_DEG  ') INFO(7) = stream
         if (field.eq.'PA_V3   ') INFO(8) = stream
         if (field.eq.'PROPOSID') INFO(9) = stream
 
         if (field.eq.'CRPIX1  ') HDR(01) = stream
         if (field.eq.'CRPIX2  ') HDR(02) = stream
         if (field.eq.'CRVAL1  ') HDR(03) = stream
         if (field.eq.'CRVAL2  ') HDR(04) = stream
         if (field.eq.'CTYPE1  ') HDR(05) = stream
         if (field.eq.'CTYPE2  ') HDR(06) = stream
         if (field.eq.'CD1_1   ') HDR(07) = stream
         if (field.eq.'CD1_2   ') HDR(08) = stream
         if (field.eq.'CD2_1   ') HDR(09) = stream
         if (field.eq.'CD2_2   ') HDR(10) = stream
         if (field.eq.'ORIENTAT') HDR(11) = stream
         if (field.eq.'PA_APER ') HDR(12) = stream
         if (field.eq.'PA_V3   ') HDR(13) = stream
         if (field.eq.'DATE-OBS') HDR(14) = stream
         if (field.eq.'TIME-OBS') HDR(15) = stream
         if (field.eq.'EXPTIME ') HDR(16) = stream
         if (field.eq.'ROOTNAME') HDR(17) = stream
         if (field.eq.'TARGNAME') HDR(18) = stream
         if (field.eq.'RA_TARG ') HDR(19) = stream
         if (field.eq.'DEC_TARG') HDR(20) = stream
         if (field.eq.'RA_DEG  ') HDR(19) = stream
         if (field.eq.'DEC_DEG ') HDR(20) = stream
         if (field.eq.'PROPOSID') HDR(21) = stream
         if (field.eq.'FILTER1 ') HDR(22) = stream
         if (field.eq.'FILTER2 ') HDR(23) = stream
         if (field.eq.'VAFACTOR') HDR(24) = stream
         if (field.eq.'CCDGAIN ') HDR(25) = stream
         if (field.eq.'END     ') then
            if (NEXTENU.gt.NEXTEND) then
               print*,'                     '
               write(*,'(''readfits_i2e: '',80a)') FILEI
               print*,'     NEXTENU.lt.NEXTEND...'
               print*,'     ---> NEXTEND: ',NEXTEND
               print*,'     ---> NEXTENU: ',NEXTENU
               print*,'                          '
               stop
               endif
            NEND = NEND + 1
            if (NEND.ge.1) goto 101
            endif
         enddo
      goto 100
 101  continue
 
      nread = nread + 1
      if (DIAG) then
         print*,' '
         print*,'----------------------------------------'
         print*,'   NREAD: ',nread
         print*,' NEXTEND: ',nextend
         print*,' NEXTENU: ',nextenu
         print*,'   NAXIS: ',naxes
         print*,'   LAXIS: ',laxis(1),laxis(2),laxis(3)
         print*,'  BITPIX: ',bitpix
         print*,'  BSCALE: ',bscale
         print*,'   BZERO: ',bzero
         print*,'   NDIMX: ',NDIMX
         print*,'   NDIMY: ',NDIMY
         print*,' '
         endif
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      NXF = laxis(1)
      NYF = laxis(2)
 
      nbper  = 2*laxis(1)*laxis(2)
      npt    =   laxis(1)*laxis(2)
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
c     print*,'NEND: ',NEND,NEXTENU,BITPIX
      if (NEND.ne.NEXTENU) goto 100
 
      if (BITPIX.ne.16) then
         print*,'prob'
         stop
         endif
 
      do i = i1, i2, 1
         read(10,rec=i,iostat=ios) buffc
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/2 + 1
         np2 = (nbyteE-nbyte1)/2 + 1
         call buff2pix_i2e(buffb,pix(1,1),np1,npt)
         if (DIAG) write(*,1115) i,np1,np2,npt,i/laxis(1)
 1115    format(1x,i8,1x,i10,1x,i10,1x,i10,1x,i6.6)
         enddo
 
 
      close(10)
      return
 
 900  continue
      print*,'READFITS_I2E ERROR'
      stop
 
      end
 
 
 
 
      subroutine buff2pix_i2e(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      integer*2 pix(*)
      integer n1,nt
 
      byte b(2)
      integer*2 ii
      equivalence(ii,b)
 
      integer i, npu, nbu
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
      do i = 1, 1440
         npu = n1+i-1
         nbu = (i-1)*2
         if (.not.LINUX_FLAG) then
            b(1) = buff(nbu+1)
            b(2) = buff(nbu+2)
            endif
         if (LINUX_FLAG) then
            b(2) = buff(nbu+1)
            b(1) = buff(nbu+2)
            endif
         if (npu.ge.1.and.npu.le.nt) pix(npu) = ii
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/writfits_r4.f"
c****                                         
c*********************************************
                                              
 
c-----------------------------------------------------
c
c this just writes a real*4 fits image
c
 
      subroutine writfits_r4(FILE,pix,PXDIMX,PXDIMY)
      implicit none
 
      character*80 FILE
      integer PXDIMX,PXDIMY
      real    pix(PXDIMX,PXDIMY)
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffb,buffc)
 
      integer ifirst, i1, i2
 
      integer np1, np2, npt
      integer k
 
      character*80 FILEU
      character*70 HDR(25)
      common/HDR/HDR
 
      FILEU = FILE
      do i = 75,2,-1
         if (FILE(i:i+4).eq.'.fits') FILEU = FILE(1:i+4)
         enddo
 
      open(10,file=FILEU,status='unknown',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      do i = 0001, 2880
         buffc(i:i) = ' '
         enddo
 
      write(buffc( 0*80+1: 1*80),'(''SIMPLE  =                    T'')')
      write(buffc( 1*80+1: 2*80),'(''BITPIX  =                  -32'')')
      write(buffc( 2*80+1: 3*80),'(''NAXIS   ='',9x,i12)') 2
      write(buffc( 3*80+1: 4*80),'(''NAXIS1  ='',9x,i12)') PXDIMX
      write(buffc( 4*80+1: 5*80),'(''NAXIS2  ='',9x,i12)') PXDIMY
      write(buffc( 5*80+1: 6*80),'(''DATATYPE='',9a)')     " 'REAL*4' "
      write(buffc(35*80+1:36*80),'(''END      '')')
 
      i = 1
      write(10,rec=i,iostat=ios) buffc
 
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      nbper  = 4*PXDIMX*PXDIMY
      npt    =   PXDIMX*PXDIMY
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
      do i = i1, i2, 1
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/4 + 1
         np2 = (nbyteE-nbyte1)/4 + 1
         call pix2buff_r4(buffb,pix,np1,npt)
         write(10,rec=i,iostat=ios) buffc
         enddo
 
      close(10)
 
      return
 
 900  continue
      print*,'writfits_r4.f ERROR'
      print*,'   FILEU: ',FILEU
      stop
 
      end
 
c-------------------------------------------------------
c
c
      subroutine pix2buff_r4(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real*4 pix(*)
      integer n1,nt
 
      byte b(4)
      real*4 r
      equivalence(r,b)
 
      integer i, npu, nbu
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (npu.ge.1.and.npu.le.nt) r = pix(npu)
         if (.not.LINUX_FLAG) then
            buff(nbu+1) = b(1)
            buff(nbu+2) = b(2)
            buff(nbu+3) = b(3)
            buff(nbu+4) = b(4)
            endif
         if (LINUX_FLAG) then
            buff(nbu+1) = b(4)
            buff(nbu+2) = b(3)
            buff(nbu+3) = b(2)
            buff(nbu+4) = b(1)
            endif
         enddo
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/readfits_r4.f"
c****                                         
c*********************************************
                                              
 
c--------------------------------------------------
c
c this just reads in an r4 fits image
c
 
      subroutine readfits_r4(FILE,pix,NDIMX,NDIMY)
      implicit none
 
      character*80 FILE
      integer NDIMX,NDIMY
      real    pix(NDIMX,NDIMY)
 
      character*80 FILEU
      character*70 INFO(10)
      common / fitsinfo / INFO
 
      integer naxes
      integer laxis(3)
      common/laxis3_/laxis
 
      character*8  field
      character*70 stream
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k
      integer j
 
      character*2880 buffc
      byte   buffb(2880)
      equivalence (buffc,buffb)
 
      real*4 buffr(0720)
      integer ii,nn,nx,ny
      integer nxx, nyy
      integer ifirst, i1, i2
 
      integer np1, np2, npt
      integer nextend
      integer nread
      real bscale, bzero
      integer bitpix
 
      logical DIAG
      data DIAG /.false./
 
      character*70 HDR(25)
      common/HDR/HDR
 
      FILEU = FILE
      do i = 75,2,-1
         if (FILE(i:i+4).eq.'.fits') FILEU = FILE(1:i+4)
         enddo
 
      do i = 1, 25
         HDR(i) = ' '
         enddo
 
 
      if (DIAG) then
         print*,'enter readfits_r4...'
         print*,'FILE: ',FILE(1:60)
         endif
 
      open(10,file=FILEU,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      if (DIAG) print*,'...opened'
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
      do i = 1, 10
         INFO(i) = ' '
         enddo
 
      i = 0
      nread = 0
 100  continue
      i = i + 1
      read(10,rec=i,iostat=ios) buffc
      if (DIAG) print*,'READREC: ',i
      do k = 0, 35, 1
         if (DIAG) write(*,'(i4,1x,i4,1x,a80)')
     .                   i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+10:k*80+79)
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (field.eq.'NAXIS3  ') read(stream,*) laxis(3)
         if (field.eq.'NEXTEND ') read(stream,*) nextend
         if (field.eq.'BITPIX  ') read(stream,*) bitpix
         if (field.eq.'BSCALE  ') read(stream,*) bscale
         if (field.eq.'BZERO   ') read(stream,*) bzero
 
         if (field.eq.'EXPTIME ') INFO(1) = stream
         if (field.eq.'FILTNAM1') INFO(2) = stream
         if (field.eq.'FILENAME') INFO(3) = stream
         if (field.eq.'DATE-OBS') INFO(4) = stream
         if (field.eq.'TIME-OBS') INFO(5) = stream
         if (field.eq.'DEC_TARG') INFO(6) = stream
         if (field.eq.'RA_TARG ') INFO(7) = stream
         if (field.eq.'PA_V3   ') INFO(8) = stream
         if (field.eq.'PROPOSID') INFO(9) = stream
 
         if (field.eq.'CRPIX1  ') HDR(01) = stream
         if (field.eq.'CRPIX2  ') HDR(02) = stream
         if (field.eq.'CRVAL1  ') HDR(03) = stream
         if (field.eq.'CRVAL2  ') HDR(04) = stream
         if (field.eq.'CTYPE1  ') HDR(05) = stream
         if (field.eq.'CTYPE2  ') HDR(06) = stream
         if (field.eq.'CD1_1   ') HDR(07) = stream
         if (field.eq.'CD1_2   ') HDR(08) = stream
         if (field.eq.'CD2_1   ') HDR(09) = stream
         if (field.eq.'CD2_2   ') HDR(10) = stream
         if (field.eq.'ORIENTAT') HDR(11) = stream
         if (field.eq.'PA_APER ') HDR(12) = stream
         if (field.eq.'PA_V3   ') HDR(13) = stream
         if (field.eq.'DATE-OBS') HDR(14) = stream
         if (field.eq.'TIME-OBS') HDR(15) = stream
         if (field.eq.'EXPTIME ') HDR(16) = stream
         if (field.eq.'ROOTNAME') HDR(17) = stream
         if (field.eq.'TARGNAME') HDR(18) = stream
         if (field.eq.'RA_TARG ') HDR(19) = stream
         if (field.eq.'DEC_TARG') HDR(20) = stream
         if (field.eq.'PROPOSID') HDR(21) = stream
         if (field.eq.'FILTER1 ') HDR(22) = stream
         if (field.eq.'FILTER2 ') HDR(23) = stream
         if (field.eq.'VAFACTOR') HDR(24) = stream
 
         if (field.eq.'END     ') goto 101
         enddo
      goto 100
 101  continue
 
      nread = nread + 1
      if (DIAG) then
         print*,'----------------------------------------'
         print*,'  NREAD: ',nread
         print*,'NEXTEND: ',nextend
         print*,'  NAXIS: ',naxes
         print*,'  LAXIS: ',laxis(1),laxis(2),laxis(3)
         print*,' BITPIX: ',bitpix
         print*,' BSCALE: ',bscale
         print*,'  BZERO: ',bzero
         endif
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      nbper  = 4*laxis(1)*laxis(2)
      npt    = laxis(1)*laxis(2)
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
      if (BITPIX.ne.-32) then
         print*,'BITPIX.ne.-32... unreal!'
         stop
         endif
 
      do i = i1, i2, 1
         read(10,rec=i,iostat=ios) buffc
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/4 + 1
         np2 = (nbyteE-nbyte1)/4 + 1
         call buff2pix_r4(buffb,buffr,0001,0720)
         do ii = 001, 720
            nn = np1 + (ii-1)
            ny = 1 + (nn-1)/laxis(1)
            nx = nn-(ny-1)*laxis(1)
            if (nx.ge.001.and.nx.le.NDIMX.and.
     .          ny.ge.001.and.ny.le.NDIMY) then
                pix(nx,ny) = buffr(ii)
                nxx = nx
                nyy = ny
                endif
            enddo
         if (ny.gt.NDIMY) goto 899
 
         if (DIAG) write(*,1115) i,np1,np2,npt,nxx,nyy
 1115    format(1x,i8,1x,i10,1x,i10,1x,i10,1x,2i6)
         enddo
 
  899 close(10)
      if (DIAG) write(*,1115) i,np1,np2,npt,nxx,nyy
 
 
 
      return
 
  900 continue
      print*,'                '
      print*,'READFITS ERROR: '
      print*,'                '
      write(*,'(''   could not read in file:   '',80a)') FILEU
      print*,'                '
      stop
 
      end
 
 
 
      subroutine buff2pix_r4(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real pix(*)
      integer n1,nt
 
      byte b(4)
      real r
      equivalence(r,b)
 
      integer i, npu, nbu
 
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (.not.LINUX_FLAG) then
            b(1) = buff(nbu+1)
            b(2) = buff(nbu+2)
            b(3) = buff(nbu+3)
            b(4) = buff(nbu+4)
            endif
         if (LINUX_FLAG) then
            b(4) = buff(nbu+1)
            b(3) = buff(nbu+2)
            b(2) = buff(nbu+3)
            b(1) = buff(nbu+4)
            endif
         if (npu.ge.1.and.npu.le.nt) pix(npu) = r
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/readfits_r4e.f"
c****                                         
c*********************************************
                                              
 
c-----------------------------------------------------------------
c
c reads an r4 fits image, with extensions (reads in one extension)
c
 
      subroutine readfits_r4e(FILE,pix,NDIMX,NDIMY,NEXTENU)
      implicit none
 
      character*80 FILE
      integer NDIMX,NDIMY
      real    pix(NDIMX,NDIMY)
      integer NEXTENU
 
      character*80 FILEU
      character*70 INFO(10)
      common / fitsinfo / INFO
 
      integer naxes
      integer laxis(3)
      common/laxis3_/laxis
 
      integer NXF
      integer NYF
 
      character*8  field
      character*40 stream
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k
      integer j
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffc,buffb)
 
      integer ifirst, i1, i2
 
      integer np1, np2, npt
      integer nextend
      integer nread
      real bscale, bzero
      integer bitpix
 
      character*70 HDR(25)
      common/HDR/HDR
 
      logical DIAG
      data DIAG /.false./
      integer NEND
      integer iend
 
      if (DIAG) then
         print*,'enter readfits_r4...'
         print*,'FILE: ',FILE(1:60)
         endif
 
      FILEU = FILE
      iend = 0
      do i = 76,1,-1
         if (DIAG) print*,i,iend,FILE(i:i+4)
         if (FILE(i:i+4).eq.'.fits') iend = i+4
         enddo
      if (DIAG) then
         print*,'iend: ',iend
         endif
      if (iend.eq.0) stop 'NO .fits in FILENAME'
      FILEU = FILE(1:iend)
 
      if (DIAG) then
         print*,'purge...'
         print*,'FILEU: ',FILEU(1:60)
         endif
 
      open(10,file=FILEU,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      if (DIAG) print*,'...opened'
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
      do i = 1, 10
         INFO(i) = ' '
         enddo
 
      BSCALE = 1.0
      BZERO  = 0.0
 
      NEND = 0
      i = 0
      nread = 0
 100  continue
      i = i + 1
      if (DIAG) print*,'READREC: ',i
      read(10,rec=i,iostat=ios) buffc
      do k = 0, 35, 1
         if (DIAG) write(*,'(i4,1x,i4,1x,a80)')
     .                   i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+11:k*80+51)
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (field.eq.'NAXIS3  ') read(stream,*) laxis(3)
         if (field.eq.'NEXTEND ') read(stream,*) nextend
         if (field.eq.'BITPIX  ') read(stream,*) bitpix
         if (field.eq.'BSCALE  ') read(stream,*) bscale
         if (field.eq.'BZERO   ') read(stream,*) bzero
 
         if (field.eq.'EXPTIME ') INFO(1) = stream
         if (field.eq.'FILTER  ') INFO(2) = stream
         if (field.eq.'FILTNAM1') INFO(2) = stream
         if (field.eq.'FILENAME') INFO(3) = stream
         if (field.eq.'DATE-OBS') INFO(4) = stream
         if (field.eq.'TIME-OBS') INFO(5) = stream
         if (field.eq.'DEC_TARG') INFO(6) = stream
         if (field.eq.'RA_TARG ') INFO(7) = stream
         if (field.eq.'PA_V3   ') INFO(8) = stream
         if (field.eq.'PROPOSID') INFO(9) = stream
 
         if (field.eq.'CRPIX1  ') HDR(01) = stream
         if (field.eq.'CRPIX2  ') HDR(02) = stream
         if (field.eq.'CRVAL1  ') HDR(03) = stream
         if (field.eq.'CRVAL2  ') HDR(04) = stream
         if (field.eq.'CTYPE1  ') HDR(05) = stream
         if (field.eq.'CTYPE2  ') HDR(06) = stream
         if (field.eq.'CD1_1   ') HDR(07) = stream
         if (field.eq.'CD1_2   ') HDR(08) = stream
         if (field.eq.'CD2_1   ') HDR(09) = stream
         if (field.eq.'CD2_2   ') HDR(10) = stream
         if (field.eq.'ORIENTAT') HDR(11) = stream
         if (field.eq.'PA_APER ') HDR(12) = stream
         if (field.eq.'PA_V3   ') HDR(13) = stream
         if (field.eq.'DATE-OBS') HDR(14) = stream
         if (field.eq.'TIME-OBS') HDR(15) = stream
         if (field.eq.'EXPTIME ') HDR(16) = stream
         if (field.eq.'ROOTNAME') HDR(17) = stream
         if (field.eq.'TARGNAME') HDR(18) = stream
         if (field.eq.'RA_TARG ') HDR(19) = stream
         if (field.eq.'DEC_TARG') HDR(20) = stream
         if (field.eq.'PROPOSID') HDR(21) = stream
         if (field.eq.'FILTER ')  HDR(22) = stream
         if (field.eq.'FILTER1 ') HDR(22) = stream
         if (field.eq.'FILTER2 ') HDR(23) = stream
         if (field.eq.'VAFACTOR') HDR(24) = stream
 
         if (field.eq.'END     ') then
           !print*,' ---> NEND: ',NEND,NEXTENU
            if (NEND.eq.NEXTENU) goto 101
            NEND = NEND + 1
            endif
         enddo
      goto 100
 101  continue
 
      nread = nread + 1
      if (DIAG) then
         print*,' '
         print*,'----------------------------------------'
         print*,'  NREAD: ',nread
         print*,'NEXTEND: ',nextend
         print*,'  NAXIS: ',naxes
         print*,'  LAXIS: ',laxis(1),laxis(2),laxis(3)
         print*,' BITPIX: ',bitpix
         print*,' BSCALE: ',bscale
         print*,'  BZERO: ',bzero
         print*,'  NDIMX: ',NDIMX
         print*,'  NDIMY: ',NDIMY
         print*,' '
         endif
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      NXF = laxis(1)
      NYF = laxis(2)
 
      nbper  = 4*laxis(1)*laxis(2)
      npt    = laxis(1)*laxis(2)
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
      if (BITPIX.ne.-32) then
         print*,'prob'
         stop
         endif
 
      do i = i1, i2, 1
         read(10,rec=i,iostat=ios) buffc
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/4 + 1
         np2 = (nbyteE-nbyte1)/4 + 1
c        call buff2pix_r4(buffb,pix,np1,npt)
         call buff2pix_r4_edge(buffb,pix,np1,npt,
     .                         NDIMX,NDIMY,laxis(1),laxis(2))
         if (DIAG) write(*,1115) i,np1,np2,npt
 1115    format(1x,i8,1x,i10,1x,i10,1x,i10)
         enddo
 
      close(10)
      return
 
 900  continue
      print*,'READFITS ERROR'
      stop
 
      end
 
 
c------------------------------------------------------
c
c
      subroutine buff2pix_r4_edge(buff,pix,n1,nt,
     .                            NXP,NYP,NXF,NYF)
      implicit none
c     character buff(2880)
      byte buff(2880)
      integer NXP,NYP
      real pix(NXP,NYP)
      integer n1,nt
      integer NXF,NYF
 
      real pbuff(720)
      common /sneaky/pbuff
      integer i
      integer npu, nbu
      integer NX, NY
 
      byte b(4)
      real r
      equivalence(r,b)
 
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (npu.ge.1.and.npu.le.nt) then
            NX = npu - (npu-1)/NXF*NXF
            NY = 1 + (npu-1)/NXF
            if (NX.le.NXP.and.NY.le.NYP) then
               if (.not.LINUX_FLAG) then
                  b(1) = buff(nbu+1)
                  b(2) = buff(nbu+2)
                  b(3) = buff(nbu+3)
                  b(4) = buff(nbu+4)
                  endif
               if (LINUX_FLAG) then
                  b(4) = buff(nbu+1)
                  b(3) = buff(nbu+2)
                  b(2) = buff(nbu+3)
                  b(1) = buff(nbu+4)
                  endif
               if (npu.ge.1.and.npu.le.nt) pix(NX,NY) = r
               endif
            endif
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/writfits_r4h.f"
c****                                         
c*********************************************
                                              
 
c--------------------------------------------------------
c
c this just writes a real*4 fits image, but with a header
c string (modulo the axis stuff...)
c
c
      subroutine writfits_r4h(FILE,pix,PXDIMX,PXDIMY,STRING_HEAD)
      implicit none
 
      character*80 FILE
      integer PXDIMX,PXDIMY
      real    pix(PXDIMX,PXDIMY)
      character*80 STRING_HEAD(360)
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffb,buffc)
 
      integer ifirst, i1, i2
 
      integer np1, np2, npt
      integer ii, page
 
      character*80 FILEU
      character*70 HDR(25)
      common/HDR/HDR
      character*70 TEMP70
 
      logical break
 
      FILEU = FILE
      do i = 75,2,-1
         if (FILE(i:i+4).eq.'.fits') FILEU = FILE(1:i+4)
         enddo
 
      open(10,file=FILEU,status='unknown',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
 
      write(buffc( 0*80+1: 1*80),'(''SIMPLE  =                    T'')')
      write(buffc( 1*80+1: 2*80),'(''BITPIX  =                  -32'')')
      write(buffc( 2*80+1: 3*80),'(''NAXIS   = '',8x,i12)') 2
      write(buffc( 3*80+1: 4*80),'(''NAXIS1  = '',8x,i12)') PXDIMX
      write(buffc( 4*80+1: 5*80),'(''NAXIS2  = '',8x,i12)') PXDIMY
      do ii = 05, 35
         write(buffc(ii*80+1:ii*80+80),'(''COMMENT   '',a05)') '     '
         enddo
c     write(buffc(35*80+1:35*80+80),'(''END'')')
      i = 1
      write(10,rec=i,iostat=ios) buffc
 
      break = .false.
      do page = 01, 10
         if (.not.break) then
            do ii = 01, 36
               if (STRING_HEAD((page-1)*36+ii)(1:3).eq.'END')
     .             break = .true.
               if (STRING_HEAD((page-1)*36+ii)(1:6).eq.'SIMPLE'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'BITPIX'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'NAXIS '.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'NAXIS1'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'NAXIS2'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'NEXTEN'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'EXTEND'.or.
     .             STRING_HEAD((page-1)*36+ii)(1:6).eq.'GROUPS') then
                   TEMP70 = STRING_HEAD((page-1)*36+ii)(01:70)
                   write(STRING_HEAD((page-1)*36+ii),
     .                   '(''COMMENT   '',a70)') TEMP70
                   endif
               buffc((ii-1)*80+01:(ii-1)*80+80) =
     .               STRING_HEAD((page-1)*36+ii)
               enddo
            i = i + 1
            write(10,rec=i,iostat=ios) buffc
            endif
         enddo
 
c     print*,'i: ',i
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      nbper  = 4*PXDIMX*PXDIMY
      npt    =   PXDIMX*PXDIMY
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
c     print*,'---> i1: ',i1
c     print*,'---> i2: ',i2
 
      do i = i1, i2, 1
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/4 + 1
         np2 = (nbyteE-nbyte1)/4 + 1
         call pix2buff_r4h(buffb,pix,np1,npt)
         write(10,rec=i,iostat=ios) buffc
         enddo
 
      close(10)
 
      return
 
 900  continue
      print*,'writfits_r4h.f ERROR'
      print*,'   FILEU: ',FILEU
      stop
 
      end
 
c-------------------------------------------------------
c
c
      subroutine pix2buff_r4h(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real*4 pix(*)
      integer n1,nt
 
      byte b(4)
      real*4 r
      equivalence(r,b)
 
      integer i, npu, nbu
 
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
      do i = 1, 720
         npu = n1+i-1
         nbu = (i-1)*4
         if (npu.ge.1.and.npu.le.nt) r = pix(npu)
         if (.not.LINUX_FLAG) then
            buff(nbu+1) = b(1)
            buff(nbu+2) = b(2)
            buff(nbu+3) = b(3)
            buff(nbu+4) = b(4)
            endif
         if (LINUX_FLAG) then
            buff(nbu+1) = b(4)
            buff(nbu+2) = b(3)
            buff(nbu+3) = b(2)
            buff(nbu+4) = b(1)
            endif
         enddo
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/fitshead2string.f"
c****                                         
c*********************************************
                                              
 
c---------------------------------------------------------
c
c this reads in the zero-header and saves it into a string
c
c
      subroutine fitshead2string(filename,string_head)
      implicit none
 
      character*80 filename
 
      character*80 string_head(360)
 
      character*2880 buff
 
      integer n, i, ios, k
 
 
c-----------------------------------------------
 
      do n = 001, 360
         string_head(n) = '                    '
         enddo
 
      open(10,file=FILENAME,status='old',
     .  err=900,recl=2880,form='UNFORMATTED',
     .  access='DIRECT')
 
      i = 0
      n = 0
 100  continue
      i = i + 1
      read(10,rec=i,iostat=ios) buff
      if (ios.lt.0) goto 900
      do k = 0, 35, 1
         n = n + 1
         if (n.gt.360) stop 'fitshead2string:  n.gt.360'
         string_head(n) = buff(k*80+01:k*80+80)
         if (string_head(n)(1:3).eq.'END') goto 101
 109     continue
         enddo
      goto 100
 101  continue
      close(10)
 
      return
 
  900 continue
      print*,' '
      print*,'fitshead2string.e ERROR EXIT. '
      print*,' '
      write(*,'(''PROBLEM FILE: '',a80)') FILENAME
      print*,' '
      stop
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/writfits_r2j.f"
c****                                         
c*********************************************
                                              
 
c-----------------------------------------------------
c
c This outputs an r*4 image into jay's ingeger*2
c format; it has BZERO = -32700 and it has *5 rescaling
c at the bright end to allow the entire dynamic range.
c
      subroutine writfits_r2j(FILE,pixr,PXDIMX,PXDIMY)
      implicit none
 
      integer PXDIMX,PXDIMY
      character*80 FILE
      real*4 pixr(PXDIMX,PXDIMY)
 
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffb,buffc)
 
      integer ifirst, i1, i2
 
      integer np1, np2, npt
 
      integer pixii
      real PA_APER
 
      character*70 HDR(25)
      common/HDR/HDR
 
 
      integer NH_RECs
      character*2880 HEADER_STRING(99)
      common /HEADER_STRING_INFO/NH_RECs,HEADER_STRING
 
      character*80 FILEU
      integer k
      character*8  FIELD
      character*80 ORIG
 
      FILEU = FILE
      do i = 75,2,-1
         if (FILE(i:i+4).eq.'.fits') FILEU = FILE(1:i+4)
         enddo
 
c     write(*,'(''ENTER   writfits_i2_32K: '',80a)') FILEU
 
      open(10,file=FILEU,
     .     status='unknown',
     .     err   =900,
     .     recl  =2880,
     .     form  ='UNFORMATTED',
     .     access='DIRECT')
 
 
      if (NH_RECs.lt.0.or.NH_RECs.gt.99) stop 'bounds NH_RECs'
      if (NH_RECs.eq.0) then
         i = 1
         write(buffc( 0*80+1: 1*80),'(''SIMPLE  = T    '')')
         write(buffc( 1*80+1: 2*80),'(''BITPIX  =  16  '')')
         write(buffc( 2*80+1: 3*80),'(''NAXIS   = '',i12)') 2
         write(buffc( 3*80+1: 4*80),'(''NAXIS1  = '',i12)') PXDIMX
         write(buffc( 4*80+1: 5*80),'(''NAXIS2  = '',i12)') PXDIMY
         write(buffc( 5*80+1: 6*80),'(''DATATYPE= '',9a)')
     .                             ' ''INTEGER*2 '''
         write(buffc( 6*80+1: 7*80),'(''DATE    = '',11a)')
     .                             ' ''28/01/00'''
         write(buffc( 7*80+1: 8*80),'(''BSCALE  = '',i12)') 00001
         write(buffc( 8*80+1: 9*80),'(''BZERO   = '',i12)') 32000
         write(buffc(09*80+1:10*80),'(''CRPIX1  = '',a20)') HDR(01)
         write(buffc(10*80+1:11*80),'(''CRPIX2  = '',a20)') HDR(02)
         write(buffc(11*80+1:12*80),'(''CRVAL1  = '',a20)') HDR(03)
         write(buffc(12*80+1:13*80),'(''CRVAL2  = '',a20)') HDR(04)
         write(buffc(13*80+1:14*80),'(''CTYPE1  = '',a20)') HDR(05)
         write(buffc(14*80+1:15*80),'(''CTYPE2  = '',a20)') HDR(06)
         write(buffc(15*80+1:16*80),'(''CD1_1   = '',a20)') HDR(07)
         write(buffc(16*80+1:17*80),'(''CD1_2   = '',a20)') HDR(08)
         write(buffc(17*80+1:18*80),'(''CD2_1   = '',a20)') HDR(09)
         write(buffc(18*80+1:19*80),'(''CD2_2   = '',a20)') HDR(10)
         write(buffc(19*80+1:20*80),'(''ORIENTAT= '',a20)') HDR(11)
         write(buffc(20*80+1:21*80),'(''PA_APER = '',a20)') HDR(12)
         write(buffc(21*80+1:22*80),'(''PA_V3   = '',a20)') HDR(13)
         write(buffc(22*80+1:23*80),'(''DATE-OBS= '',a20)') HDR(14)
         write(buffc(23*80+1:24*80),'(''TIME-OBS= '',a20)') HDR(15)
         write(buffc(24*80+1:25*80),'(''EXPTIME = '',a20)') HDR(16)
         write(buffc(25*80+1:26*80),'(''ROOTNAME= '',a20)') HDR(17)
         write(buffc(26*80+1:27*80),'(''TARGNAME= '',a20)') HDR(18)
         write(buffc(27*80+1:28*80),'(''RA_TARG = '',a20)') HDR(19)
         write(buffc(28*80+1:29*80),'(''DEC_TARG= '',a20)') HDR(20)
         write(buffc(29*80+1:30*80),'(''PROPOSID= '',a20)') HDR(21)
         write(buffc(30*80+1:31*80),'(''FILTER1 = '',a20)') HDR(22)
         write(buffc(31*80+1:32*80),'(''FILTER2 = '',a20)') HDR(23)
         write(buffc(32*80+1:33*80),'(''VAFACTOR= '',a20)') HDR(24)
         write(buffc(33*80+1:34*80),'(''COMMENT   '')')
         write(buffc(34*80+1:35*80),'(''COMMENT   '')')
         write(buffc(35*80+1:36*80),'(''END       '')')
         write(10,rec=i,iostat=ios) buffc
         ifirst = i+1
         i1 = i
         i2 = i
         endif
 
      if (NH_RECs.gt.0) then
         do k = 1, 36
            buffc(1+(k-1)*80:80+(k-1)*80) = 'COMMENT'
            enddo
         write(buffc( 0*80+1: 1*80),'(''SIMPLE  = T    '')')
         write(buffc( 1*80+1: 2*80),'(''BITPIX  =  16  '')')
         write(buffc( 2*80+1: 3*80),'(''NAXIS   = '',i12)') 2
         write(buffc( 3*80+1: 4*80),'(''NAXIS1  = '',i12)') PXDIMX
         write(buffc( 4*80+1: 5*80),'(''NAXIS2  = '',i12)') PXDIMY
         write(buffc( 5*80+1: 6*80),'(''DATATYPE= '',9a)')
     .                             ' ''INTEGER*2 '''
         write(buffc( 6*80+1: 7*80),'(''BSCALE  = '',i12)') 00001
         write(buffc( 7*80+1: 8*80),'(''BZERO   = '',i12)') 32000
         read(HDR(12),*,end=3) PA_APER
         write(buffc( 8*80+1: 9*80),'(''PA_APER = '',f12.4)') PA_APER
    3    continue
         write(10,rec=1,iostat=ios) buffc
         do i = 1, NH_RECs
            do k = 01, 36
               ORIG  = HEADER_STRING(i)(1+(k-1)*80:80+(k-1)*80)
               FIELD = HEADER_STRING(i)(1+(k-1)*80:08+(k-1)*80)
               if (FIELD.eq.'SIMPLE  '.or.
     .             FIELD.eq.'NEXTEND '.or.
     .             FIELD.eq.'EXTEND  '.or.
     .             FIELD.eq.'BITPIX  '.or.
     .             FIELD.eq.'EXTEND  '.or.
     .             FIELD.eq.'NAXIS   '.or.
     .             FIELD.eq.'NAXIS1  '.or.
     .             FIELD.eq.'NAXIS2  '.or.
     .             FIELD.eq.'DATATYPE'.or.
     .             FIELD.eq.'BSCALE  '.or.
     .             FIELD.eq.'BZERO   ')
     .             HEADER_STRING(i)(01+(k-1)*80:80+(k-1)*80) = ' '
               write(*,'(i2,1x,i2,5x,a80,10x,a80)') i,k,ORIG,
     .               HEADER_STRING(i)(1+(k-1)*80:80+(k-1)*80)
               enddo
            write(*,'(''    IN: '',a80)') HEADER_STRING(i)
            write(10,rec=i+1,iostat=ios) HEADER_STRING(i)
            enddo
         i = NH_RECs + 1
         ifirst = i+1
         i1 = i
         i2 = i
         endif
 
      nbper  = 2*PXDIMX*PXDIMY
      npt    =   PXDIMX*PXDIMY
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
      do i = i1, i2, 1
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/4 + 1
         np2 = (nbyteE-nbyte1)/4 + 1
         np1 = (nbyte0-nbyte1)/2 + 1
         np2 = (nbyteE-nbyte1)/2 + 1
         call pix2buff_r2j(buffb,pixr,np1,npt)
         write(10,rec=i,iostat=ios) buffc
         enddo
 
      close(10)
 
      return
 
 900  continue
      print*,'WRITFITS.f ERROR'
      stop
 
      end
 
 
 
 
      subroutine pix2buff_r2j(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      real*4 pix(*)
      integer n1,nt
 
      byte b(2)
      integer*2 ii
      equivalence(ii,b)
 
      integer i, npu, nbu
      integer pixii
      real rr
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
 
      do i = 1, 1440
         npu = n1+i-1
         nbu = (i-1)*2
         rr = 0.0
         if (npu.ge.1.and.npu.le.nt) rr = pix(npu)
         pixii = int(1000+rr+0.5)
         pixii = pixii - 1000
         if (pixii.gt.55000) then
            pixii = 55000 + (pixii-55000+2)/5
            endif
         pixii = pixii - 32000
         if (pixii.lt.-32750) pixii = -32750
         if (pixii.gt. 32750) pixii =  32750
         ii = pixii
         if (.not.LINUX_FLAG) then
            buff(nbu+1) = b(1)
            buff(nbu+2) = b(2)
            endif
         if (LINUX_FLAG) then
            buff(nbu+1) = b(2)
            buff(nbu+2) = b(1)
            endif
         enddo
 
      return
      end
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/readfits_j2r.f"
c****                                         
c*********************************************
                                              
 
cc-----------------------------------------------------
c
c This reads in an image in jay's integer*2 format into
c a real*4 pixel array
c
      subroutine readfits_j2r(FILE,pix,NX,NY)
      implicit none
 
      character*80 FILE
      integer NX, NY
      real*4 pix(NX,NY)
 
      character*70 INFO(10)
      common / fitsinfo / INFO
 
      integer naxes
      integer laxis(3)
 
      character*8  field
      character*20 stream
 
      real*4 pixu
      integer nbyte0
      integer nbyteE
      integer nbyte1
      integer nbyte2
      integer nbper
      integer i,ios, k
      integer ii, jj
      integer n
      integer NXU, NYU
 
      character*2880 buffc
      byte buffb(2880)
      equivalence (buffc,buffb)
 
      integer*2 ibuff(1440)
 
      integer ifirst, i1, i2
      integer j
 
      integer np1, np2, npt
      integer nextend
      integer nread
      real bscale, bzero
      integer bitpix
 
      integer r2i
 
      logical DIAG
      data DIAG /.false./
 
 
      character*70 HDR(25)
      common/HDR/HDR
      character*80 FILEU
 
      FILEU = FILE
      do i = 75,2,-1
         if (FILE(i:i+4).eq.'.fits') FILEU = FILE(1:i+4)
         enddo
 
 
 
      open(10,file=FILEU,status='old',
     .     err=900,recl=2880,form='UNFORMATTED',
     .     access='DIRECT')
 
      if (DIAG) print*,'...opened'
 
      bscale = 1
      bzero  = 0
 
      naxes = -1
      laxis(1) = 1
      laxis(2) = 1
      laxis(3) = 1
      nextend = 0
 
      do i = 1, 10
         INFO(i) = ' '
         enddo
      do i = 1, 25
         HDR(i) = ' '
         enddo
      HDR(24) = '  1.000 '
 
      i = 0
      nread = 0
 100  continue
      i = i + 1
      read(10,rec=i,iostat=ios) buffc
      if (DIAG) print*,'READREC: ',i
      do k = 0, 35, 1
         if (DIAG) write(*,'(i4,1x,i4,1x,a80)')
     .                   i,k,buffc(k*80+1:k*80+80)
         field  = buffc(k*80+01:k*80+08)
         stream = buffc(k*80+11:k*80+31)
         if (field.eq.'NAXIS   ') read(stream,*) naxes
         if (field.eq.'NAXIS1  ') read(stream,*) laxis(1)
         if (field.eq.'NAXIS2  ') read(stream,*) laxis(2)
         if (field.eq.'NAXIS3  ') read(stream,*) laxis(3)
         if (field.eq.'NEXTEND ') read(stream,*) nextend
         if (field.eq.'BITPIX  ') read(stream,*) bitpix
         if (field.eq.'BSCALE  ') read(stream,*) bscale
         if (field.eq.'BZERO   ') read(stream,*) bzero
 
         if (field.eq.'EXPTIME ') INFO(01) = stream
         if (field.eq.'FILTNAM1') INFO(02) = stream
         if (field.eq.'FILENAME') INFO(03) = stream
         if (field.eq.'DATE-OBS') INFO(04) = stream
         if (field.eq.'TIME-OBS') INFO(05) = stream
         if (field.eq.'DEC_TARG') INFO(06) = stream
         if (field.eq.'RA_TARG ') INFO(07) = stream
         if (field.eq.'PA_V3   ') INFO(08) = stream
         if (field.eq.'PROPOSID') INFO(09) = stream
         if (field.eq.'CCDGAIN ') INFO(10) = stream
 
         if (field.eq.'CRPIX1  ') HDR(01) = stream
         if (field.eq.'CRPIX2  ') HDR(02) = stream
         if (field.eq.'CRVAL1  ') HDR(03) = stream
         if (field.eq.'CRVAL2  ') HDR(04) = stream
         if (field.eq.'CTYPE1  ') HDR(05) = stream
         if (field.eq.'CTYPE2  ') HDR(06) = stream
         if (field.eq.'CD1_1   ') HDR(07) = stream
         if (field.eq.'CD1_2   ') HDR(08) = stream
         if (field.eq.'CD2_1   ') HDR(09) = stream
         if (field.eq.'CD2_2   ') HDR(10) = stream
         if (field.eq.'ORIENTAT') HDR(11) = stream
         if (field.eq.'PA_APER ') HDR(12) = stream
         if (field.eq.'PA_V3   ') HDR(13) = stream
         if (field.eq.'DATE-OBS') HDR(14) = stream
         if (field.eq.'TIME-OBS') HDR(15) = stream
         if (field.eq.'EXPTIME ') HDR(16) = stream
         if (field.eq.'ROOTNAME') HDR(17) = stream
         if (field.eq.'TARGNAME') HDR(18) = stream
         if (field.eq.'RA_TARG ') HDR(19) = stream
         if (field.eq.'DEC_TARG') HDR(20) = stream
         if (field.eq.'PROPOSID') HDR(21) = stream
         if (field.eq.'FILTER  ') HDR(22) = stream
         if (field.eq.'FILTER  ') HDR(23) = stream
         if (field.eq.'FILTER1 ') HDR(22) = stream
         if (field.eq.'FILTER2 ') HDR(23) = stream
         if (field.eq.'VAFACTOR') HDR(24) = stream
 
         if (field.eq.'END     ') goto 101
         enddo
      goto 100
 101  continue
 
      nread = nread + 1
      if (DIAG) then
         print*,'----------------------------------------'
         print*,'  NREAD: ',nread
         print*,'NEXTEND: ',nextend
         print*,'  NAXIS: ',naxes
         print*,'  LAXIS: ',laxis(1),laxis(2),laxis(3)
         print*,' BITPIX: ',bitpix
         print*,' BSCALE: ',bscale
         print*,'  BZERO: ',bzero
         endif
 
      ifirst = i+1
      i1 = i
      i2 = i
 
      if (BITPIX.ne.16) then
         print*,'readfits_i2...: '
         print*,'                '
         print*,'   you called a routine to read in an'
         print*,'   unsigned i2 image, and the image you'
         print*,'   gave it has BITPIX = ',BITPIX
         print*,'   '
         print*,'   FILEU: ',FILEU
         print*,'   '
         stop
         endif
 
      nbper = 2*laxis(1)*laxis(2)
      npt   =   laxis(1)*laxis(2)
      nbyte1 = 1
      nbyte2 = nbper
      i1 = i+1 + nbyte1/2880
      i2 = i+1 + nbyte2/2880
 
      if (laxis(1).gt.NX.and.laxis(2).gt.NY) then
         print*,' not enough image space! '
         print*,' '
         print*,'  laxis1: ',laxis(1)
         print*,'      NX: ',NX
         print*,' '
         print*,'  laxis2: ',laxis(2)
         print*,'      NY: ',NY
         print*,' '
         stop
         endif
 
      NXU = laxis(1)
      NYU = laxis(2)
 
      if (DIAG) then
         print*,'     NX: ',NX
         print*,'     NY: ',NY
         print*,'  NBPER: ',nbper
         print*,'  NBYT1: ',nbyte1
         print*,'  NBYT2: ',nbyte2
         print*,' IFIRST: ',ifirst
         print*,'     I1: ',i1
         print*,'     I2: ',i2
         print*,'    NPT: ',NPT
         endif
      do i = i1, i2, 1
         read(10,rec=i,iostat=ios) buffc
         nbyte0 = (i-ifirst)*2880+   1
         nbyteE = (i-ifirst)*2880+2880
         np1 = (nbyte0-nbyte1)/2 + 1
         np2 = (nbyteE-nbyte1)/2 + 1
         np2 = min(np2,npt)
         call buff2pix_i2r(buffb,ibuff,0001,1440)
         do n = np1, np2, 1
            jj = n/NXU   + 1
            ii = n-NXU*(jj-1)
            pixu = ibuff(n-np1+1)*bscale+bzero
            if (pixu.gt.55000) pixu = 55000 + (pixu-55000)*5
            pix(ii,jj) = pixu
            enddo
         enddo
 
      if (DIAG) then
         print*,'  NBPER: ',nbper
         print*,'  NBYT1: ',nbyte1
         print*,'  NBYT2: ',nbyte2
         print*,' IFIRST: ',ifirst
         print*,'     I1: ',i1
         print*,'     I2: ',i2
         print*,'    NPT: ',NPT
         endif
 
 
      return
 
 900  continue
      print*,'READFITS_I2 ERROR'
      print*,'    FILE: ',FILE
      stop
 
      end
 
 
 
      subroutine buff2pix_i2r(buff,pix,n1,nt)
      implicit none
      byte buff(2880)
      integer*2 pix(*)
      integer n1,nt
 
      byte b(2)
      integer*2 ii
      equivalence(ii,b)
 
      integer i, npu, nbu
      logical LINUX_FLAG
      common /LINUX_/LINUX_FLAG
 
 
      do i = 1, 1440
         npu = n1+i-1
         nbu = (i-1)*2
         if (.not.LINUX_FLAG) then
            b(1) = buff(nbu+1)
            b(2) = buff(nbu+2)
            endif
         if (LINUX_FLAG) then
            b(2) = buff(nbu+1)
            b(1) = buff(nbu+2)
            endif
         if (npu.ge.1.and.npu.le.nt) pix(npu) = ii
         enddo
 
      return
      end
 
 
                                              
c*********************************************
c****                                         
c**** #include "../ROUTINES/query_hdr.f"
c****                                         
c*********************************************
                                              
 
c---------------------------------------------------
c
c This routine checks to see if the header of an image
c contains a particular keyword. If it does, it returns
c its value-string in STREAMX.
c
 
      subroutine query_hdr(filename,FIELDX,streamx)
      implicit none
 
      character*80 filename
 
      character*8  field
      character*20 stream
 
      character*8  fieldx
      character*20 streamx
 
      integer  i
      integer ios, k
 
      character*2880 buff
 
      integer nread
 
 
c-----------------------------------------------
 
      !print*,'query_hdr...',FILENAME
      !print*,'    fieldx: ',fieldx
      streamx = ' '
 
      close(10)
      open(10,file=FILENAME,status='old',
     .  err=900,recl=2880,form='UNFORMATTED',
     .  access='DIRECT')
 
      streamx = 'NULL'
      i = 0
      nread = 0
 100  continue
      i = i + 1
      read(10,rec=i,iostat=ios) buff
      if (ios.lt.0) goto 900
      do k = 0, 35, 1
         field  = buff(k*80+01:k*80+08)
         stream = buff(k*80+11:k*80+31)
         !print*,i,k,field,stream
         if (field.eq.fieldx) streamx = stream(1:20)
         if (field.eq.'END     ') goto 101
 109     continue
         enddo
      goto 100
 101  continue
      close(10)
      !print*,'    streamx: ',streamx
 
      return
 
  900 continue
      print*,' '
      print*,'imginfo.e ERROR EXIT. '
      print*,' '
      print*,'ONE OF THE IMAGES WAS NOT IN STANDARD'
      print*,'HST FITS FORMAT.'
      print*,' '
      write(*,'(''PROBLEM FILE: '',a80)') FILENAME
      print*,' '
      stop
      end



c-----------------------------------------------
c
c Returns rval if rval is between rlo and rhi,
c otherwise it returns the closer endpoint.  It
c also make sure rval is not a NaN
c
      real function rclip(rval,rlo,rhi)
      implicit none

      real rval
      real rlo
      real rhi

      rclip = rval
      if (rclip.gt.rhi) rclip = rhi
      if (rclip.lt.rlo) rclip = rlo
      if (.not.(rclip.lt.rhi).and.
     .    .not.(rclip.gt.rlo)) rclip = rhi

      return
      end


 
