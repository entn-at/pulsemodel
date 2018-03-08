import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'external/pyworld/pyworld'))

import unittest

import numpy as np
np.random.seed(123)

filenames = ['slt_arctic_a0010.wav', 'bdl_arctic_a0020.wav', 'clb_arctic_a0030.wav', 'awb_arctic_a0040.wav']

def run_command(cmd):
    ret = os.system(cmd)
    if ret!=0: raise ValueError('Command "'+cmd+'" exited with error code '+str(ret))

class TestSmoke(unittest.TestCase):
    def test_smoke_cmd_analysis(self):
        fname = filenames[0] # Just with one file for smoke test

        run_command('python analysis.py test/'+fname)
        run_command('python analysis.py test/'+fname+' --f0_min 75 --f0 test/'+fname.replace('.wav','.f0'))
        run_command('python analysis.py test/'+fname+' --f0_max 200 --f0 test/'+fname.replace('.wav','.f0'))
        run_command('python analysis.py test/'+fname+' --f0_min 81 --f0_max 220 --f0 test/'+fname.replace('.wav','.f0'))
        run_command('python analysis.py test/'+fname+' --f0 test/'+fname.replace('.wav','.f0'))
        run_command('python analysis.py test/'+fname+' --inf0bin test/'+fname.replace('.wav','.f0')+' --spec test/'+fname.replace('.wav','.spec'))
        run_command('python analysis.py test/'+fname+' --f0_log  --f0 test/'+fname.replace('.wav','.lf0'))
        run_command('python analysis.py test/'+fname+' --spec test/'+fname.replace('.wav','.spec'))
        # run_command('python analysis.py test/'+fname+' --spec_mceporder 60 --spec test/'+fname.replace('.wav','.spec')) # Need SPTK for this one
        run_command('python analysis.py test/'+fname+' --spec_nbfwbnds 65 --spec test/'+fname.replace('.wav','.fwlspec'))
        run_command('python analysis.py test/'+fname+' --pdd test/'+fname.replace('.wav','.pdd'))
        # run_command('python analysis.py test/'+fname+' --pdd_mceporder 60 --pdd test/'+fname.replace('.wav','.pdd'))  # Need SPTK for this one
        run_command('python analysis.py test/'+fname+' --nm test/'+fname.replace('.wav','.nm'))
        run_command('python analysis.py test/'+fname+' --nm_nbfwbnds 33 --nm test/'+fname.replace('.wav','.fwnm'))

        # TODO Test various sampling fromats, encoding and sampling rates for wav files

    def test_smoke_cmd_synthesis(self):
        fname = filenames[0] # Just with one file for smoke test

        run_command('python synthesis.py test/'+fname.replace('.wav','.resynth.wav')+' --fs 16000 --f0 test/'+fname.replace('.wav','.f0')+' --spec test/'+fname.replace('.wav','.spec'))
        run_command('python synthesis.py test/'+fname.replace('.wav','.resynth.wav')+' --fs 16000 --logf0 test/'+fname.replace('.wav','.lf0')+' --spec test/'+fname.replace('.wav','.spec'))
        run_command('python synthesis.py test/'+fname.replace('.wav','.resynth.wav')+' --fs 16000 --f0 test/'+fname.replace('.wav','.f0')+' --spec test/'+fname.replace('.wav','.spec')+' --pdd test/'+fname.replace('.wav','.pdd'))
        run_command('python synthesis.py test/'+fname.replace('.wav','.resynth.wav')+' --fs 16000 --f0 test/'+fname.replace('.wav','.f0')+' --spec test/'+fname.replace('.wav','.spec')+' --nm test/'+fname.replace('.wav','.nm'))
        run_command('python synthesis.py test/'+fname.replace('.wav','.resynth.wav')+' --fs 16000 --logf0 test/'+fname.replace('.wav','.lf0')+' --fwlspec test/'+fname.replace('.wav','.fwlspec')+' --fwnm test/'+fname.replace('.wav','.fwnm'))

    # def test_smoke_analysisf(self):
    #     fname = filenames[0] # Just with one file for smoke test
    #     import pulsemodel
    #
    #     f0_min = 75
    #     f0_max = 800
    #
    #     pulsemodel.analysisf(fname, f0_min=f0_min, f0_max=f0_max, ff0=fname.replace('.wav','.lf0'), f0_log=True,
    #     fspec=fname.replace('.wav','.fwlspec'), spec_nbfwbnds=65, fnm=fname.replace('.wav','.fwnm'), nm_nbfwbnds=33, verbose=1)

    def test_smoke_analysis_synthesis(self):
        fname = filenames[0] # Just with one file for smoke test

        f0_min = 75
        f0_max = 800
        shift = 0.010
        verbose = 1
        dftlen = 512

        import pulsemodel
        import sigproc as sp

        wav, fs, enc = sp.wavread('test/'+fname)

        f0s, SPEC, PDD, NM = pulsemodel.analysis(wav, fs)

        _ = pulsemodel.analysis_f0postproc(wav, fs, f0s=np.zeros(f0s[:,1].shape), f0_min=f0_min, f0_max=f0_max, shift=shift, verbose=verbose)

        _ = pulsemodel.analysis_f0postproc(wav, fs, f0s=f0s[:,1], f0_min=f0_min, f0_max=f0_max, shift=shift, verbose=verbose)

        nonunif0s = f0s.copy()
        nonunif0s[:,0] = np.random.rand(f0s.shape[0])*(f0s[-1,0]-f0s[0,0]) + f0s[0,0]
        nonunif0s[:,0] = np.sort(nonunif0s[:,0])
        _ = pulsemodel.analysis_f0postproc(wav, fs, f0s=nonunif0s, f0_min=f0_min, f0_max=f0_max, shift=shift, verbose=verbose)

        f0s = pulsemodel.analysis_f0postproc(wav, fs, f0_min=f0_min, f0_max=f0_max, shift=shift, verbose=verbose)

        f0_min = 60
        f0_max = 600
        shift = 0.005
        dftlen = 4096
        f0s, SPEC, PDD, NM = pulsemodel.analysis(wav, fs, f0s=f0s, f0_min=f0_min, f0_max=f0_max, shift=shift, dftlen=dftlen, verbose=verbose)


        import pulsemodel
        syn = pulsemodel.synthesize(fs, f0s, SPEC, wavlen=len(wav))

        syn = pulsemodel.synthesize(fs, f0s, SPEC, NM=NM, wavlen=len(wav))

        NM = PDD.copy()
        NM[NM>0.75] = 1
        NM[NM<=0.75] = 0
        syn = pulsemodel.synthesize(fs, f0s, SPEC, NM=NM, wavlen=len(wav))

        syn = pulsemodel.synthesize(fs, f0s, SPEC, NM=NM, wavlen=len(wav)
                        , ener_multT0=True
                        , nm_cont=True, nm_lowpasswinlen=13, hp_f0coef=0.25, antipreechohwindur=0.002
                        , pp_f0_rmsteps=True, pp_f0_smooth=0.100, pp_atten1stharminsilences=-25
                        , verbose=verbose)

    def test_repeatability(self):

        f0_min = 60
        f0_max = 600

        import pulsemodel
        # import pyworld
        # import sigproc as sp

        for fname in filenames:
            fname = 'test/'+fname
            lf0s_ref = None
            pwf0_ref = None
            SPEC_ref = None
            fwlspec_ref = None
            fwnm_ref = None
            for _ in xrange(2):
                print('Extracting features for: '+fname)
                pulsemodel.analysisf(fname, f0_min=f0_min, f0_max=f0_max, ff0=fname.replace('.wav','.lf0'), f0_log=True,
                fspec=fname.replace('.wav','.fwlspec'), spec_nbfwbnds=65, fnm=fname.replace('.wav','.fwnm'), nm_nbfwbnds=33, verbose=1)


                lf0s = np.fromfile(fname.replace('.wav','.lf0'), dtype=np.float32)
                lf0s = lf0s.reshape((-1, 1))
                print('lf0 sum square: '+str(np.sum((lf0s)**2)))

                if lf0s_ref is None:
                    lf0s_ref = lf0s
                else:
                    diff = np.sum((lf0s_ref-lf0s)**2)
                    print('lf0 diff: '+str(diff))
                    self.assertEqual(diff, 0.0)


                # #_f0, ts = pyworld.dio(x, fs, frame_period=shift*1000)    # raw pitch extractor # Use REAPER instead
                # wav, fs, enc = sp.wavread(fname)
                #
                # pwts = 0.005*np.arange(len(lf0s)) # TODO TODO TODO 0.005
                # dftlen = 4096
                # # from IPython.core.debugger import  Pdb; Pdb().set_trace()
                # dlf0s = lf0s.astype(np.float64)
                # pwf0 = pyworld.stonemask(wav, np.ascontiguousarray(np.exp(dlf0s[:,0])), pwts, fs)  # pitch refinement
                # if pwf0_ref is None:
                #     pwf0_ref = pwf0
                # else:
                #     print('pwf0 diff: '+str(np.sum((pwf0_ref-pwf0)**2)))
                #
                # SPEC = pyworld.cheaptrick(wav, pwf0, pwts, fs, fft_size=dftlen)  # extract smoothed spectrogram
                # if SPEC_ref is None:
                #     SPEC_ref = SPEC
                # else:
                #     print('SPEC diff: '+str(np.sum((SPEC_ref-SPEC)**2)))


                fwlspec = np.fromfile(fname.replace('.wav','.fwlspec'), dtype=np.float32)
                fwlspec = fwlspec.reshape((-1, 65))
                print('fwlspec sum square: '+str(np.sum((fwlspec)**2)))

                if fwlspec_ref is None:
                    fwlspec_ref = fwlspec
                else:
                    diff = np.sum((fwlspec_ref-fwlspec)**2)
                    print('fwlspec diff: '+str(diff))
                    self.assertEqual(diff, 0.0)


                fwnm = np.fromfile(fname.replace('.wav','.fwnm'), dtype=np.float32)
                fwnm = fwnm.reshape((-1, 33))
                print('fwnm sum square: '+str(np.sum((fwnm)**2)))

                if fwnm_ref is None:
                    fwnm_ref = fwnm
                else:
                    diff = np.sum((fwnm_ref-fwnm)**2)
                    print('fwnm diff: '+str(diff))
                    self.assertEqual(diff, 0.0)


if __name__ == '__main__':
    unittest.main()
