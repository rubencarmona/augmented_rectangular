OutDir  = [pwd filesep '..' filesep 'RunDss' filesep];

lcode=fopen([OutDir 'linecode.txt'],'w');

mytext1=('New LineCode.%d nphases=4 baseFreq=50 units=km\r\n');
mytext2=('~ rmatrix = [%f | 0     %f  |  0  0   %f |  0  0  0 %f]\r\n');
mytext3=('~ xmatrix = [ %f| 0     %f  |  0  0   %f|  0  0  0 %f]\r\n');


code=zeros(length(Segment),1);

%%%%%  R_A   X_A     R_UG   X_UG   
R_X=[9.9   0.075    9.9    0.075  % 2 mm Cu
     4.95   0.075    4.95   0.075 % 4 mm Cu
     3.30   0.075    3.30   0.075 % 6 mm cu
     1.23   0.08     1.23   0.08  % 16 mm Cu
     2.14   0.09     2.14   0.09  %16 mm Al
     1.34   0.097    1.538  0.095 %25 mm Cu
     0.9073 0.095    0.907318 0.095 % 35 mm Al
     0.718497 0.093 0.718497 0.093 %50 mm Al
     0.6579 0.09    0.6579   0.09 %54.6 mm Al
     0.4539  0.091   0.515   0.085 %70 mm AL
     0.39 0.090 0.4506 0.084 % 80 mm Al
     0.358688  0.089  0.410272  0.083  %95 mm Al
     0.230905 0.085 0.264113 0.082  % 150 mm Al
     0.160263 0.079 0.160263 0.079 % 240 mm Al
     0.21  0.075    0.21   0.075  %Desconcido
];
%types of Conductor with Phase and neutral
%%%%%%%%%% code  R_phase  X_phase   R_Neutral  X_Neutral
Conductor=[250  R_X(15,1)  R_X(15,2) R_X(15,1)  R_X(15,2) %Aereal BT - Desconocido BT
           350  R_X(15,3)  R_X(15,4) R_X(15,3)  R_X(15,4) %Underground BT - Desconocido BT
           201  R_X(4,1)  R_X(4,2) R_X(4,1)  R_X(4,2) %Aereal BT - MANGUERA
           301  R_X(4,3)  R_X(4,4) R_X(4,3)  R_X(4,4) %UG BT - MANGUERA
           202  R_X(5,1)  R_X(5,2) R_X(5,1)  R_X(5,2)% Aereal BT - RV 0,6/1 KV 2*16 KAL
           302  R_X(5,3)  R_X(5,4) R_X(5,3)  R_X(5,4)  %UG  BT - RV 0,6/1 KV 2*16 KAL
           203  R_X(6,1)  R_X(6,2) R_X(6,1)  R_X(6,2)%Aereal BT - RV 0,6/1 KV 2*25 KAL
   303  R_X(6,3)  R_X(6,4) R_X(6,3)  R_X(6,4)%UG BT - RV 0,6/1 KV 2*25 KAL
   204  R_X(13,1)  R_X(13,2) R_X(12,1)  R_X(12,2)% Aereal BT - RV 0,6/1 KV 3(1*150 KAL) + 1*95 KAL
   304  R_X(13,3)  R_X(13,4)  R_X(12,3)  R_X(12,4) % UG BT - RV 0,6/1 KV 3(1*150 KAL) + 1*95 KAL
   205  R_X(14,1)  R_X(14,2) R_X(13,1)  R_X(13,2) %Aeral BT - RV 0,6/1 KV 3(1*240 KAL) + 1*150 KAL
   305  R_X(14,3)  R_X(14,4) R_X(13,3)  R_X(13,4)  %UG BT - RV 0,6/1 KV 3(1*240 KAL) + 1*150 KAL
   206  R_X(14,1)  R_X(14,2) R_X(12,1)  R_X(12,2)%Aer BT - RV 0,6/1 KV 3(1*240 KAL) + 1*95 KAL
   306  R_X(14,3)  R_X(14,4) R_X(12,3)  R_X(12,4) %UG BT - RV 0,6/1 KV 3(1*240 KAL) + 1*95 KAL
   207  R_X(6,1)  R_X(6,2) R_X(6,1)  R_X(6,2) %Aer BT - RV 0,6/1 KV 4*25 KAL
   307  R_X(6,3)  R_X(6,4) R_X(6,3)  R_X(6,4)%UG  BT - RV 0,6/1 KV 4*25 KAL
   208  R_X(8,1)  R_X(8,2) R_X(8,1)  R_X(8,2) %Aer BT - RV 0,6/1 KV 4*50 KAL
   308  R_X(8,3)  R_X(8,4) R_X(8,3)  R_X(8,4)%UG BT - RV 0,6/1 KV 4*50 KAL
   209  R_X(12,1)  R_X(12,2) R_X(12,1)  R_X(12,2) % Aer BT - RV 0,6/1 KV 4*95 KAL
   309  R_X(12,3)  R_X(12,4) R_X(12,3)  R_X(12,4)%UG BT - RV 0,6/1 KV 4*95 KAL
   210 R_X(4,1)  R_X(4,2) R_X(4,1)  R_X(4,2) %BT - RX 0,6/1 KV 2*16 Cu
   310  R_X(4,3)  R_X(4,4) R_X(4,3)  R_X(4,4) %UG  RX 0,6/1 KV 2*16 Cu
   211 R_X(1,1)  R_X(1,2) R_X(1,1)  R_X(1,2) %AerealBT - RX 0,6/1 KV 2*2 Cu00
   311  R_X(1,3)  R_X(1,4) R_X(1,3)  R_X(1,4) %Underground BT - RX 0,6/1 KV 2*2 Cu00
   212  R_X(2,1)  R_X(2,2) R_X(2,1)  R_X(2,2) %AerealBT - RX 0,6/1 KV 2*4 Cu
   312  R_X(2,3)  R_X(2,4) R_X(2,3)  R_X(2,4) %Underground BT - RX 0,6/1 KV 2*4 Cu
   213  R_X(3,1)  R_X(3,2) R_X(3,1)  R_X(3,2) %Aereal BT - RX 0,6/1 KV 2*6 Cu
   313  R_X(3,3)  R_X(3,4) R_X(3,3)  R_X(3,4) %Underground  BT - RX 0,6/1 KV 2*4 Cu
   214  R_X(5,1)  R_X(5,2) R_X(5,1)  R_X(5,2) % Aereal BT - RZ 0,6/1 KV 2*16 AL
   314  R_X(5,3)  R_X(5,4) R_X(5,3)  R_X(5,4)  %UG BT - RZ 0,6/1 KV 2*16 AL
   215  R_X(13,1)  R_X(13,2) R_X(11,1)  R_X(11,2)% Aereal BT - RZ 0,6/1 KV 3*150 AL/80 ALM0
   315  R_X(13,3)  R_X(13,4)  R_X(11,3)  R_X(11,4) % UG BT - RZ 0,6/1 KV 3*150 AL/80 ALM0
   216  R_X(13,1)  R_X(13,2) R_X(12,1)  R_X(12,2)% Aereal BT - RZ 0,6/1 KV 3*150 AL/95 ALM
   316  R_X(13,3)  R_X(13,4)  R_X(12,3)  R_X(12,4) % UG BT - RZ 0,6/1 KV 3*150 AL/95 ALM
   217  R_X(6,1)  R_X(6,2) R_X(9,1)  R_X(9,2) %Aereal BT - RZ 0,6/1 KV 3*25 AL/54,6 ALM
   317  R_X(6,3)  R_X(6,4) R_X(9,3)  R_X(9,4)%UG BT - RZ 0,6/1 KV 3*25 AL/54,6 ALM
   218  R_X(7,1)  R_X(7,2) R_X(9,1)  R_X(9,2) %Aereal BT - RZ 0,6/1 KV 3*35 AL/54,6 ALM
   318  R_X(7,3)  R_X(7,4) R_X(9,3)  R_X(9,4)%UG BT - RZ 0,6/1 KV 3*35 AL/54,6 ALM
   219  R_X(8,1)  R_X(8,2) R_X(9,1)  R_X(9,2) %Aereal BT - RZ 0,6/1 KV 3*50 AL/54,6 ALM
   319  R_X(8,3)  R_X(8,4) R_X(9,3)  R_X(9,4)%UG BT - RZ 0,6/1 KV 3*35 AL/54,6 ALM
   220  R_X(10,1)  R_X(10,2) R_X(9,1)  R_X(9,2) %Aereal BT - RZ 0,6/1 KV 3*70 ALM/54,6 AL
   320  R_X(10,3)  R_X(10,4) R_X(9,3)  R_X(9,4)%UG BT - RZ 0,6/1 KV 3*70 ALM/54,6 AL
   221  R_X(12,1)  R_X(12,2) R_X(9,1)  R_X(9,2) %Aereal BT - RZ 0,6/1 KV 3*95 AL/54,6 ALM
   321  R_X(12,3)  R_X(12,4) R_X(9,3)  R_X(9,4)%UG  BT - RZ 0,6/1 KV 3*95 AL/54,6 ALM
   222   R_X(5,1)  R_X(5,2) R_X(5,1)  R_X(5,2) % Aereal%Aereal BT - RZ 0,6/1 KV 4*16 AL
   322  R_X(5,3)  R_X(5,4) R_X(5,3)  R_X(5,4)  %UG BT - RZ 0,6/1 KV 4*16 AL
   ];

for i=1:46
    fprintf(lcode,mytext1,Conductor(i,1));
    fprintf(lcode,mytext2,Conductor(i,2),Conductor(i,2),Conductor(i,2),Conductor(i,4));
    fprintf(lcode,mytext3,Conductor(i,3),Conductor(i,3),Conductor(i,3),Conductor(i,5));
end
%line constant for HT line line code 101
RHT=0.05;
XHT=0.05;
fprintf(lcode,'New LineCode.%d nphases=3 baseFreq=50 units=km\r\n',101);
fprintf(lcode,'~ rmatrix = [%f | 0     %f  |  0  0   %f] \r\n',RHT,RHT,RHT);
fprintf(lcode,'~ xmatrix = [ %f| 0     %f  |  0  0   %f] \r\n',XHT,XHT,XHT);

%lineconstant for fuse circuit breaker line code 102

R_fuse=0.05; %per km
X_fuse=0.05; % per km
    fprintf(lcode,mytext1,102);
    fprintf(lcode,mytext2,R_fuse,R_fuse,R_fuse,R_fuse);
    fprintf(lcode,mytext3,X_fuse,X_fuse,X_fuse,X_fuse);
for i=1:length(Segment)
    if Segraw{i+1,3}(1)=='A'
          if strcmp(Segraw{i+1,8},'BT - MANGUERA')
            code(i)=201;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*2 Cu')
                code(i)=210;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*4 Cu')
                code(i)=211;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*6 Cu')
                code(i)=212; 
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*16 Cu')
                code(i)=213;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 2*16 AL')
                code(i)=214;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 4*16 AL')
                code(i)=222;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 2*16 KAL')
                code(i)=202;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 2*25 KAL')
                code(i)=203;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*25 KAL')
                code(i)=207;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*50 KAL')
                code(i)=208;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*95 KAL')
                code(i)=209;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*150 AL/80 ALM')
                code(i)=215;
             elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*150 AL/95 ALM')
                code(i)=216;
             elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*35 AL/54,6 ALM')
                code(i)=218;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*50 AL/54,6 ALM')
                code(i)=219;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*70 ALM/54,6 AL')
                code(i)=220;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*95 AL/54,6 ALM')
                code(i)=221;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*25 AL/54,6 ALM')
                code(i)=217;
           elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*150 KAL) + 1*95 KAL')
                code(i)=204;
          elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*240 KAL) + 1*95 KAL')
                code(i)=206;
          elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*240 KAL) + 1*150 KAL')
                code(i)=205;
          else
            code(i)=250;
       end
 elseif Segraw{i+1,3}(1)=='S'
         if strcmp(Segraw{i+1,8},'BT - MANGUERA')
                code(i)=301;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*2 Cu')
                code(i)=310;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*4 Cu')
                code(i)=311;
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*6 Cu')
                code(i)=312; 
            elseif strcmp(Segraw{i+1,8},'BT - RX 0,6/1 KV 2*16 Cu')
                code(i)=313;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 2*16 AL')
                code(i)=314;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 4*16 AL')
                code(i)=322;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 2*16 KAL')
                code(i)=302;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 2*25 KAL')
                code(i)=303;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*25 KAL')
                code(i)=307;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*50 KAL')
                code(i)=308;
            elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 4*95 KAL')
                code(i)=309;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*150 AL/80 ALM')
                code(i)=315;
             elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*150 AL/95 ALM')
                code(i)=316;
             elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*35 AL/54,6 ALM')
                code(i)=318;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*50 AL/54,6 ALM')
                code(i)=319;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*70 ALM/54,6 AL')
                code(i)=320;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*95 AL/54,6 ALM')
                code(i)=321;
            elseif strcmp(Segraw{i+1,8},'BT - RZ 0,6/1 KV 3*25 AL/54,6 ALM')
                code(i)=317;
           elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*150 KAL) + 1*95 KAL')
                code(i)=304;
          elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*240 KAL) + 1*95 KAL')
                code(i)=306;
          elseif strcmp(Segraw{i+1,8},'BT - RV 0,6/1 KV 3(1*240 KAL) + 1*150 KAL')
                code(i)=305;
          else
            code(i)=350;
       end
end

end 


fclose(lcode);
%{
New LineCode.2c_.007 nphases=4 baseFreq=50 units=km
~ rmatrix = [3.97 | 0     3.97  |  0  0   3.97 |  0  0  0 3.97]
~ xmatrix = [ 0.099| 0     0.099  |  0  0   0.099|  0  0  0 0.099]
New LineCode.2c_.0225 nphases=4 baseFreq=50 units=km
~ rmatrix = [1.257 | 0     1.257  |  0  0   1.257 |  0  0  0 1.257]
~ xmatrix = [ 0.085| 0     0.085  |  0  0   0.085 |  0  0  0   0.085] 
New LineCode.2c_16 nphases=4 baseFreq=50 units=km
~ rmatrix = [1.15 | 0     1.15  |  0  0   1.15 |  0  0  0  1.15]
~ xmatrix = [ 0.088| 0   0.088  |  0  0   0.088|  0  0  0  0.088]
New LineCode.35_SAC_XSC nphases=4 baseFreq=50 units=km
~ rmatrix = [0.868 | 0     0.868  |  0  0   0.868 |  0  0  0  0.868]
~ xmatrix = [ 0.092| 0   0.092  |  0  0   0.092|  0  0  0  0.092]  

%}
