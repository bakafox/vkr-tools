
* Encoding: UTF-8.


*Spielberger STATE 

RECODE sp1,sp2,sp5,sp8,sp10,sp11,sp15,sp16,sp19,sp20 (4=1)(3=2)(2=3)(1=4) INTO spp1, spp2, spp5, spp8, spp10, spp11, spp15, spp16, spp19, spp20.
EXECUTE . 

COMPUTE SAI = 20*MEAN.10(spp1,spp2,sp3,sp4,spp5,sp6,sp7,spp8,sp9,spp10,spp11,sp12,sp13,sp14,spp15,spp16,sp17,sp18,spp19,spp20) .
EXECUTE .

RELIABILITY
  /VARIABLES=spp1 spp2 sp3 sp4 spp5 sp6 sp7 spp8 sp9 spp10 spp11 sp12 sp13 sp14 spp15 spp16 sp17 sp18 spp19 spp20
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL =ALPHA
  /SUMMARY=TOTAL .


RECODE sp1_do_EEG,sp2_do_EEG,sp5_do_EEG,sp8_do_EEG,sp10_do_EEG,sp11_do_EEG,sp15_do_EEG,sp16_do_EEG,sp19_do_EEG,sp20_do_EEG (4=1)(3=2)(2=3)(1=4) INTO spp1_do_EEG,
 spp2_do_EEG, spp5_do_EEG, spp8_do_EEG, spp10_do_EEG, spp11_do_EEG, spp15_do_EEG, spp16_do_EEG, spp19_do_EEG, spp20_do_EEG.
EXECUTE . 

COMPUTE SAI_do_EEG = 20*MEAN.10(spp1_do_EEG,spp2_do_EEG,sp3_do_EEG,sp4_do_EEG,spp5_do_EEG,sp6_do_EEG,sp7_do_EEG,spp8_do_EEG,sp9_do_EEG,spp10_do_EEG,spp11_do_EEG,
sp12_do_EEG,sp13_do_EEG,sp14_do_EEG,spp15_do_EEG,spp16_do_EEG,sp17_do_EEG,sp18_do_EEG,spp19_do_EEG,spp20_do_EEG) .
EXECUTE .


*Spielberger STATE 

RECODE sp1_do_v1,sp2_do_v1,sp5_do_v1,sp8_do_v1,sp10_do_v1,sp11_do_v1,sp15_do_v1,sp16_do_v1,sp19_do_v1,sp20_do_v1  (4=1)(3=2)(2=3)(1=4) INTO
 spp1_do_v1, spp2_do_v1, spp5_do_v1, spp8_do_v1, spp10_do_v1, spp11_do_v1, spp15_do_v1, spp16_do_v1, spp19_do_v1, spp20_do_v1.
EXECUTE . 

COMPUTE SAI_do_v1 = 20*MEAN.10(spp1_do_v1,spp2_do_v1,sp3_do_v1,sp4_do_v1,spp5_do_v1,sp6_do_v1,sp7_do_v1,spp8_do_v1,sp9_do_v1,spp10_do_v1,spp11_do_v1,sp12_do_v1,sp13_do_v1,sp14_do_v1,spp15_do_v1,spp16_do_v1,
sp17_do_v1,sp18_do_v1,spp19_do_v1,spp20_do_v1) .
EXECUTE .

*_v2

RECODE sp1_do_v2,sp2_do_v2,sp5_do_v2,sp8_do_v2,sp10_do_v2,sp11_do_v2,sp15_do_v2,sp16_do_v2,sp19_do_v2,sp20_do_v2  (4=1)(3=2)(2=3)(1=4) INTO
 spp1_do_v2, spp2_do_v2, spp5_do_v2, spp8_do_v2, spp10_do_v2, spp11_do_v2, spp15_do_v2, spp16_do_v2, spp19_do_v2, spp20_do_v2.
EXECUTE . 

COMPUTE SAI_do_v2 = 20*MEAN.10(spp1_do_v2,spp2_do_v2,sp3_do_v2,sp4_do_v2,spp5_do_v2,sp6_do_v2,sp7_do_v2,spp8_do_v2,sp9_do_v2,spp10_do_v2,spp11_do_v2,sp12_do_v2,sp13_do_v2,sp14_do_v2,spp15_do_v2,spp16_do_v2,
sp17_do_v2,sp18_do_v2,spp19_do_v2,spp20_do_v2) .
EXECUTE .


*Spielberger TRAIT  

RECODE
  ST2, ST3, ST4, ST5, ST8, ST9, ST11, ST12, ST14, ST15, ST17, ST18, ST20 (4=1)(3=2)(2=3)(1=4)  INTO STT2, STT3, STT4, STT5, STT8, STT9, STT11, STT12, STT14, STT15, STT17, STT18, STT20 .
EXECUTE .

COMPUTE STAI = 20*MEAN.10(ST1, STT2, STT3, STT4, STT5, ST6, ST7,STT8, STT9, ST10,  STT11, STT12, ST13, STT14, STT15, ST16, STT17, STT18, ST19, STT20) .
EXECUTE .

RELIABILITY
  /VARIABLES=ST1 STT2 STT3 STT4 STT5 ST6 ST7 STT8 STT9 ST10  STT11 STT12 ST13 STT14 STT15 ST16 STT17 STT18 ST19 STT20
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

Старая, реверсивная версия (неправильная) - чтобы было с чем сравнить.

RECODE
  ST1, ST3, ST6, ST7, ST10, ST13, ST14, ST16, ST19 (4=1)(3=2)(2=3)(1=4)  INTO  STT1,  STT3, STT6, STT7, STT10, STT13, STT14, STT16, STT19 .
EXECUTE .

COMPUTE Spiel_trait_r = 20*MEAN.10(STT1, ST2, STT3, ST4, ST5, STT6, STT7,ST8, ST9, STT10,  ST11, ST12, STT13, STT14, ST15, STT16, ST17, ST18, STT19, ST20) .
EXECUTE .

RELIABILITY
  /VARIABLES=STT1 ST2 STT3 ST4 ST5 STT6 STT7 ST8 ST9 STT10  ST11 ST12 STT13 STT14 ST15 STT16 ST17 ST18 STT19 ST20
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .


*BASS-PERRY

RECODE
bp9 bp16 
  (5=1)(4=2)(3=3)(2=4)(1=5) INTO  rbp9 rbp16  .
EXECUTE .   
                                                       
COMPUTE anger = 7*MEAN.(bp1,rbp9,bp12,bp18,bp19,bp23,bp28) .
EXECUTE .

COMPUTE physag = 9*MEAN.(bp2,bp5,bp8,bp11,bp13,rbp16,bp22,bp25,bp29) .
EXECUTE .

COMPUTE hostil = 8*MEAN.(bp3,bp7,bp10,bp15,bp17,bp20,bp24,bp26) .
EXECUTE .

COMPUTE verbag = 5*MEAN.(bp4,bp6,bp14,bp21,bp27) .
EXECUTE .

RELIABILITY
  /VARIABLES=bp1 rbp9 bp12 bp18 bp19 bp23 bp28
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
  /VARIABLES=bp2 bp5 bp8 bp11 bp13 rbp16 bp22 bp25 bp29
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
  /VARIABLES=bp3 bp7 bp10 bp15 bp17 bp20 bp24 bp26
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
  /VARIABLES=bp4 bp6 bp14 bp21 bp27
  /FORMAT=NOLABELS
  /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .     

*Eysenck Personality Profiler

RECODE
  ai11 ai17 ai52 ai112 ai121 ai160 ai185 ai70 ai72 ai81 ai85 ai111 ai127 ai186 ai7 ai16 ai35 ai68 ai73 ai82 ai138 ai157 ai175 ai194 ai29 ai39 ai87
  ai181 ai83 ai107 ai128 ai158 ai30 ai42 ai46 ai58 ai103 ai105 ai137 ai155 ai163 ai172 ai190 ai27 ai63 ai65 ai108 ai124 ai32 ai54 ai62 ai93 ai101 ai130
  ai140 ai142 ai184 ai26 ai38 ai41 ai67 ai78 ai113 ai125 ai134 ai139 ai143 ai161 ai164 ai165 ai171 ai180 ai88 (3=1)  (2=2)  (1=3)  INTO  air11  air17  
  air52  air112  air121  air160 air185  air70  air72  air81  air85  air111  air127  air186  air7  air16 air35  air68  air73  air82  air138  air157  air175  
  air194  air29  air39 air87  air181  air83  air107  air128  air158  air30  air42  air46  air58 air103  air105  air137  air155  air163  air172  air190  air27  
  air63  air65 air108  air124  air32  air54  air62  air93  air101  air130  air140  air142 air184  air26  air38  air41  air67  air78  air113  air125  air134  air139
  air143  air161  air164  air165  air171  air180 air88 .
EXECUTE .

*Sociability

COMPUTE SOC = 16*MEAN.8(ai10, air11, ai13, air17, ai60, ai80, ai106, air112, ai114, ai122, ai145, ai147, ai183, air185, ai188, ai195) .
EXECUTE .

*ACT
 
COMPUTE ACT = 12*MEAN.6(ai19, ai22, ai31, ai55, ai57, air72, air111, ai141, ai152, ai166, air186, ai196) .
EXECUTE .

 *ASSERT

COMPUTE ASSERT = 13*MEAN.6(ai8, air16, air35, air68, air73, ai76, air82, ai129, ai146, ai154, air157, ai168, ai179) .
EXECUTE .

*ANX
 
COMPUTE ANX = 16*MEAN.8(ai1, ai18, ai20, ai25, ai28, air29, ai34, ai43, ai47, ai51, ai61, ai102, ai135, ai151, ai156, ai191) .
EXECUTE .

*INFER
 
COMPUTE INFER = 19*MEAN.10(ai2, ai4, ai14, ai24, air39, ai49, ai50, ai86, air87, ai96, ai97, ai109, ai115, ai159, ai162, ai173, ai174, air181, ai198) .
EXECUTE .

*UNH

COMPUTE UNH = 19*MEAN.9(ai21, ai23, ai56, ai66, ai75, air83, ai90, ai92, ai94, ai99, air107, ai118, ai119, air128, ai144, ai149, ai169, ai170, ai187) .
EXECUTE .

*RISK

COMPUTE RISK = 11*MEAN.6(ai59, ai71, ai84, air103, air105, ai126, ai132, air155, air163, ai192, ai199) .
EXECUTE .
 
*IMPULS

COMPUTE IMP = 17*MEAN.8(ai3, air27, ai36, ai37, ai40, ai53, air63, air65, ai69, ai74, ai77, ai95, air108, ai117, air124, ai148, ai153) .
EXECUTE .
 
*IRRESP

COMPUTE IRRESP = 17*MEAN.9(ai12, air32, ai44, ai45, air54, air62, ai64, ai79, ai89, air93, ai98, air101, air130, air140, ai177, air184, ai197) .
EXECUTE .

*LIE

COMPUTE LIE = 17*MEAN.8(ai6, air26, air38, air41, air67, air113, air125, ai131, air134, air139, air143, air161, air164, air165, air171, air180, ai193) .
EXECUTE .

COMPUTE ExtrEPP = SOC + ACT + ASSERT .
EXECUTE .

COMPUTE NeurEPP = ANX + INFER + UNH .
EXECUTE .

COMPUTE PsychEPP = RISK + IMP + IRRESP .
EXECUTE .

RELIABILITY
   /VARIABLES= ai10 air11 ai13 air17 ai60 ai80 ai106 air112 ai114 ai122 ai145 ai147 ai183 air185 ai188 ai195
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
   /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= ai19 ai22 ai31 ai55 ai57 air72 air111 
         ai141 ai152 ai166 air186 ai196  
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= ai8 air16 air35 air68 air73 ai76 air82 ai129 ai146 ai154 air157 ai168 ai179    
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=ai1 ai18 ai20 ai25 ai28 air29 ai34 ai43 ai47 ai51 ai61 ai102  
        ai135 ai151 ai156 ai191 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=ai2 ai4 ai14 ai24 air39 ai49 ai50 ai86 air87 ai96 ai97 ai109 ai115 ai159 ai162
        ai173 ai174 air181 ai198 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

 RELIABILITY
   /VARIABLES=ai21 ai23 ai56 ai66 ai75 air83 ai90 ai92 ai94 ai99 air107 ai118 ai119 air128
        ai144 ai149 ai169 ai170 ai187
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= ai59 ai71 ai84 air103 air105 ai126 ai132 
         air155 air163 ai192 ai199
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

 RELIABILITY
   /VARIABLES=ai3 air27 ai36 ai37 ai40 ai53 air63 air65 ai69 ai74 ai77 ai95 air108 ai117 air124 ai148 ai153 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
   /SUMMARY=TOTAL .

 RELIABILITY
   /VARIABLES=ai12 air32 ai44 ai45 air54 air62 ai64 ai79 ai89 air93 ai98 air101 air130 air140 ai177 air184 ai197 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
   /SUMMARY=TOTAL .

 RELIABILITY
   /VARIABLES=ai6 air26 air38 air41 air67 air113 air125 ai131 air134 air139 air143 
       air161 air164 air165 air171 air180 ai193
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

*Goldberg 50

Extraversion: 1, 6R, 11, 16R, 21, 26R, 31, 36R, 41, 46
Agreeableness: 2R, 7, 12R, 17, 22R, 27, 32R, 37, 42, 47 
Consc: 3, 8R, 13, 18R, 23, 28R, 33, 38R, 43, 48
Neuroticism: 4, 9R, 14, 19R, 24, 29, 34, 39, 44, 49
Intellect: 5, 10R, 15, 20R, 25, 30R, 35, 40, 45, 50


RECODE
  gld6 gld16 gld26 gld36 gld2 gld12 gld22 gld32 gld8 gld18 gld28 gld38 gld9 gld19 gld10 gld20 gld30 (5=1)(4=2)(3=3)(2=4)(1=5) INTO 
  rgld6 rgld16 rgld26 rgld36 rgld2 rgld12 rgld22 rgld32 rgld8 rgld18 rgld28 rgld38 rgld9 rgld19 rgld10 rgld20 rgld30  .
EXECUTE . 

COMPUTE Extr_Gldb = 10*MEAN.(gld1,rgld6,gld11,rgld16,gld21,rgld26,gld31,rgld36,gld41,gld46) .
EXECUTE .

COMPUTE Agr_Gldb = 10*MEAN.(rgld2,gld7,rgld12,gld17,rgld22,gld27,rgld32,gld37,gld42,gld47) .
EXECUTE .

COMPUTE Cons_Gldb = 10*MEAN.(gld3,rgld8,gld13,rgld18,gld23,rgld28,gld33,rgld38,gld43,gld48) .
EXECUTE .

COMPUTE Neur_Gldb = 10*MEAN.(gld4,rgld9,gld14,rgld19,gld24,gld29,gld34,gld39,gld44,gld49) .
EXECUTE .

COMPUTE Intel_Gldb = 10*MEAN.(gld5,rgld10,gld15,rgld20,gld25,rgld30,gld35,gld40,gld45,gld50) .
EXECUTE .

RELIABILITY
   /VARIABLES=gld1 rgld6 gld11 rgld16 gld21 rgld26 gld31 rgld36 gld41 gld46
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=rgld2 gld7 rgld12 gld17 rgld22 gld27 rgld32 gld37 gld42 gld47
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=gld3 rgld8 gld13 rgld18 gld23 rgld28 gld33 rgld38 gld43 gld48
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=gld4 rgld9 gld14 rgld19 gld24 gld29 gld34 gld39 gld44 gld49
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=gld5 rgld10 gld15 rgld20 gld25 rgld30 gld35 gld40 gld45 gld50
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

Split by median

RECODE 
  Neur_Gldb
 (Lowest thru 33.00=0) (34.00 thru Highest=1)  INTO neu_split .
EXECUTE .

RECODE 
 Extr_Gldb  
 (Lowest thru 32.00=0)  (32.50 thru Highest=1)  INTO ext_split .
EXECUTE .

RECODE 
 Cons_Gldb  
 (Lowest thru 31.50=0) (32.00 thru Highest=1)  INTO cons_split .
EXECUTE .

RECODE 
 Agr_Gldb 
 (Lowest thru 37.50=0) (38.00 thru Highest=1)  INTO agr_split .
EXECUTE .

RECODE 
 Intel_Gldb  
 (Lowest thru 37.50=0) (38.00 thru Highest=1)  INTO intel_split .
EXECUTE .


*Goldberg 100 -> 50

RECODE 
  gldb1 gldb22 gldb3 gldb4 gldb5 gldb26 gldb7 gldb8 gldb9 gldb10 gldb11 gldb2 gldb13 gldb14 gldb15 gldb16 gldb17 gldb18 
  gldb19 gldb20 gldb21 gldb12 gldb23 gldb24 gldb25 gldb26 gldb27 gldb28 gldb34 gldb30 gldb31 gldb32 gldb33 gldb34 gldb35 gldb36 
  gldb37 gldb38 gldb54 gldb45 gldb41 gldb47 gldb43 gldb59 gldb55 gldb46 gldb57 gldb53 gldb64 gldb65 (ELSE=Copy) INTO gld1 gld2 
  gld3 gld4 gld5 gld6 gld7 gld8 gld9 gld10 gld11 gld12 gld13 gld14 gld15 gld16 gld17 gld18 gld19 gld20 gld21 gld22 gld23 gld24 gld25 
  gld26 gld27 gld28 gld29 gld30 gld31 gld32 gld33 gld34 gld35 gld36 gld37 gld38 gld39 gld40 gld41 gld42 gld43 gld44 gld45 gld46 gld47
  gld48 gld49 gld50 .
EXECUTE .


*Goldberg 100

RECODE
  gldb2 gldb4 gldb6 gldb8 gldb10 gldb12 gldb14 gldb16 gldb18 gldb20 gldb22 gldb24 gldb26 gldb28 gldb30 gldb32 gldb34 gldb36 
  gldb38 gldb40 gldb42 gldb44 gldb46 gldb48 gldb50 gldb52 gldb54 gldb56 gldb58 gldb59 gldb60 gldb64 gldb66 gldb68 gldb69 gldb70 
  gldb74 gldb76 gldb78 gldb79 gldb84 gldb86 gldb88 gldb89 gldb91 gldb94 gldb99 (5=1)(4=2)(3=3)(2=4)(1=5) INTO rgldb2 rgldb4 rgldb6 
  rgldb8 rgldb10 rgldb12 rgldb14 rgldb16 rgldb18 rgldb20 rgldb22 rgldb24 rgldb26 rgldb28 rgldb30 rgldb32 rgldb34 rgldb36 rgldb38 rgldb40 
  rgldb42 rgldb44 rgldb46 rgldb48 rgldb50 rgldb52 rgldb54 rgldb56 rgldb58 rgldb59 rgldb60 rgldb64 rgldb66 rgldb68 rgldb69 rgldb70 rgldb74 
 rgldb76 rgldb78 rgldb79 rgldb84 rgldb86 rgldb88 rgldb89 rgldb91 rgldb94 rgldb99 .
EXECUTE . 

COMPUTE extr_gld100 = 20*MEAN.(gldb1,rgldb6,gldb11,rgldb16,gldb21,rgldb26,gldb31,rgldb36,gldb41,rgldb46,gldb51,rgldb56,gldb61,rgldb66,
 gldb71,rgldb76,gldb81,rgldb86,rgldb91,gldb96) .
EXECUTE .

COMPUTE agr_gld100 = 20*MEAN.(rgldb2,gldb7,rgldb12,gldb17,rgldb22,gldb27,rgldb32,gldb37,gldb42,gldb47,rgldb52,gldb57,gldb62,gldb67,gldb72,
 gldb77,gldb82,gldb87,gldb92,gldb97) .
EXECUTE .

COMPUTE cons_gld100 = 20*MEAN.(gldb3,rgldb8,gldb13,rgldb18,gldb23,rgldb28,gldb33,rgldb38,gldb43,rgldb48,gldb53,rgldb58,gldb63,rgldb68,
 gldb73,rgldb78,gldb83,rgldb88,gldb93,gldb98) .
EXECUTE .


COMPUTE neur_gld100 = 20*MEAN.(rgldb4,gldb9,rgldb14,gldb19,rgldb24,gldb29,rgldb34,gldb39,rgldb44,gldb49,rgldb54,rgldb59,rgldb64,rgldb69,
 rgldb74,rgldb79,rgldb84,rgldb89,rgldb94,rgldb99) .
EXECUTE .

COMPUTE intel_gld100 = 20*MEAN.(gldb5,rgldb10,gldb15,rgldb20,gldb25,rgldb30,gldb35,rgldb40,gldb45,rgldb50,gldb55,rgldb60,gldb65,rgldb70,
 gldb75,gldb80,gldb85,gldb90,gldb95,gldb100) .
EXECUTE .

RELIABILITY
   /VARIABLES=gldb1 rgldb6 gldb11 rgldb16 gldb21 rgldb26 gldb31 rgldb36 gldb41 rgldb46 gldb51 rgldb56 gldb61 rgldb66 
   gldb71 rgldb76 gldb81 rgldb86 rgldb91 gldb96
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=rgldb2 gldb7 rgldb12 gldb17 rgldb22 gldb27 rgldb32 gldb37 gldb42 gldb47 rgldb52 gldb57 gldb62 gldb67 gldb72 
   gldb77 gldb82 gldb87 gldb92 gldb97
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=gldb3 gldb8 gldb13 rgldb18 gldb23 rgldb28 gldb33 rgldb38 gldb43 rgldb48 gldb53 rgldb58 gldb63 rgldb68 
   gldb73 rgldb78 gldb83 rgldb88 gldb93 gldb98
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=rgldb4 gldb9 rgldb14 gldb19 rgldb24 gldb29 rgldb34 gldb39 rgldb44 gldb49 rgldb54 rgldb59 rgldb64 rgldb69 
   rgldb74 rgldb79 rgldb84 rgldb89 rgldb94 rgldb99
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=gldb5 rgldb10 gldb15 rgldb20 gldb25 rgldb30 gldb35 rgldb40 gldb45 rgldb50 gldb55 rgldb60 gldb65 rgldb70 
   gldb75 gldb80 gldb85 gldb90 gldb95 gldb100
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .



*GWPQ

RECODE
  gwq3 gwq9 gwq14 gwq18 gwq21 gwq26 gwq30 gwq35 (2=0)(1=1)(0=2)  INTO  rgwq3 rgwq9 rgwq14 rgwq18 rgwq21 rgwq26 rgwq30 rgwq35 .
EXECUTE .   
                                                       
COMPUTE fight_gwpq = 16*MEAN.(gwq1,rgwq3,gwq6,rgwq9,gwq12,rgwq14,gwq16,rgwq18,gwq19,rgwq21,gwq23,rgwq26,gwq28,rgwq30,gwq32,rgwq35) .
EXECUTE .

RELIABILITY
   /VARIABLES=gwq1 rgwq3 gwq6 rgwq9 gwq12 rgwq14 gwq16 rgwq18 gwq19 rgwq21 gwq23 rgwq26 gwq28 rgwq30 gwq32 rgwq35 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

*BASgw/BISgw

RECODE
  gwq2 gwq4 gwq5 gwq8 gwq9 gwq13 gwq15 gwq20 gwq21 gwq25 gwq27 gwq31 gwq33 (2=0)(1=1)(0=2)  INTO  rgwq2 rgwq4 rgwq5 rgwq8 rgwq9 
  rgwq13 rgwq15 rgwq20 rgwq21 rgwq25 rgwq27 rgwq31 rgwq33 .
EXECUTE .  
                                                        
COMPUTE bas_gwpq = 12*MEAN.(gwq1, rgwq5, gwq7, rgwq9, gwq11, rgwq15, gwq19, rgwq21, gwq23, gwq24, rgwq27, rgwq33) .
EXECUTE .

COMPUTE bis_gwpq = 12*MEAN.(rgwq2, rgwq4, rgwq8, gwq10, rgwq13, gwq17, rgwq20, gwq22, rgwq25, gwq29, rgwq31, gwq34) .
EXECUTE .

RELIABILITY
   /VARIABLES=gwq1 rgwq5 gwq7 rgwq9 gwq11 rgwq15 gwq19 rgwq21 gwq23 gwq24 rgwq27 rgwq33 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=rgwq2 rgwq4 rgwq8 gwq10 rgwq13 gwq17 rgwq20 gwq22 rgwq25 gwq29 rgwq31 gwq34 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .




*BDI-II

RECODE bdi_16 bdi_18 (0 = 0) (1 through 2=1) (3 through 4=2) (5 through 6 =3) INTO bdi_16r bdi_18r. 
EXECUTE .

COMPUTE bdi_sum = SUM(bdi_1, bdi_2, bdi_3, bdi_4, bdi_5, bdi_6, bdi_7, bdi_8, bdi_9, bdi_10, bdi_11, 
bdi_12, bdi_13, bdi_14, bdi_15, bdi_16r, bdi_17, bdi_18r, bdi_19, bdi_20, bdi_21) .
EXECUTE .

COMPUTE bdi_aff=SUM(bdi_2,bdi_3,bdi_5,bdi_6,bdi_7,bdi_8,bdi_9,bdi_14).
EXECUTE.

COMPUTE bdi_som=SUM(bdi_1,bdi_4,bdi_10,bdi_11,bdi_12,bdi_13,bdi_15,bdi_16r,bdi_17,bdi_18r,bdi_19,bdi_20,bdi_21).
EXECUTE.


RELIABILITY
   /VARIABLES=bdi_1 bdi_2 bdi_3 bdi_4 bdi_5 bdi_6 bdi_7 bdi_8 bdi_9 bdi_10 bdi_11 
   bdi_12 bdi_13 bdi_14 bdi_15 bdi_16r bdi_17 bdi_18r bdi_19 bdi_20 bdi_21
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=bdi_2 bdi_3 bdi_5 bdi_6 bdi_7 bdi_8 bdi_9 bdi_14
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=bdi_1 bdi_4 bdi_10 bdi_11 bdi_12 bdi_13 bdi_15 bdi_16r bdi_17 bdi_18r bdi_19 bdi_20 bdi_21
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .


*EMIN

RECODE
  emi7 emi20 emi34 emi2 emi15 emi29 emi43 emi59 emi9 emi22 emi36 emi51 emi66 emi4 emi17 emi31 emi46 emi11 emi25 emi38 emi53 emi56 emi19
  emi33 emi48 emi63 emi13 emi27 emi41 emi55 emi68 (5=1)(4=2)(3=3)(2=4)(1=5) INTO rem7 rem20 rem34 rem2 rem15 rem29 rem43 rem59 rem9
  rem22 rem36 rem51 rem66 rem4 rem17 rem31 rem46 rem11 rem25 rem38 rem53 rem56 rem19 rem33 rem48 rem63 rem13 rem27 rem41 rem55 rem68 .
EXECUTE .

COMPUTE pos_expr_emin = 9*MEAN (emi1, emi14, emi28, emi42, emi49, emi58, rem7, rem20, rem34 ) .
EXECUTE .

COMPUTE neg_expr_emin = 10*MEAN (emi8, emi21,emi35, emi50, emi65, rem2, rem15, rem29, rem43, rem59 ) .
EXECUTE .

COMPUTE att_emot_emin = 10*MEAN (emi3, emi16, emi30, emi44, emi60, rem9, rem22, rem36, rem51, rem66 ) . 
EXECUTE .

COMPUTE des_emot_emin = 9*MEAN (emi10, emi23, emi37, emi52, emi61, rem4, rem17, rem31, rem46 ) .
EXECUTE .

COMPUTE joy_emp_emin = 10*MEAN (emi5, emi6, emi18, emi32, emi47, emi62, rem11, rem25, rem38, rem53 ) .
EXECUTE .

COMPUTE mis_emp_emin = 10*MEAN (emi12, emi26, emi40, emi54, emi67, rem56, rem19, rem33, rem48, rem63 ) .
EXECUTE .

COMPUTE empathy_emin = 10*MEAN (emi39, emi45, emi24, emi57, emi64, rem13, rem27, rem41, rem55, rem68 ) .
EXECUTE .

RELIABILITY
   /VARIABLES= emi1 emi14 emi28 emi42 emi49 emi58 rem7 rem20 rem34 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= emi8 emi21 emi35 emi50 emi65 rem2 rem15 rem29 rem43 rem59  
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=  emi3 emi16 emi30 emi44 emi60 rem9 rem22 rem36 rem51 rem66 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= emi10 emi23 emi37 emi52 emi61 rem4 rem17 rem31 rem46 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= emi5 emi6 emi18 emi32 emi47 emi62 rem11 rem25 rem38 rem53
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES=  emi12 emi26 emi40 emi54 emi67 rem56 rem19 rem33 rem48 rem63 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .

RELIABILITY
   /VARIABLES= emi39 emi45 emi24 emi57 emi64 rem13 rem27 rem41 rem55 rem68 
   /FORMAT=NOLABELS
   /SCALE(ALPHA)=ALL/MODEL=ALPHA
  /SUMMARY=TOTAL .


