#!/usr/bin/env python

import os
import random
import shutil
import sys
import time

class Features(object):
    '''Configuration parameters for different models''' 

    __slots__ = "lm", "wp", "tm", "glue", "d", "dg", "r", "w", "h", "rm"


def args():
    import optparse
    optparser = optparse.OptionParser(usage="usage: cat input | %prog [options]")

    optparser.add_option("", "--config", dest="configFile", type="string", help="Configuration file")
    optparser.add_option("", "--one-nt-decode", dest="one_nt_decode", default=False, action="store_true", help="Run decoder in 1NT mode (ignore 2NT rules)")
    optparser.add_option("", "--shallow-hiero", dest="shallow_hiero", default=False, action="store_true", help="Flag for shallow decoding")
    optparser.add_option("", "--shallow-order", dest="sh_order", default=1, type="int", help="Shallow decoding order")
    optparser.add_option("", "--free-glue", dest="free_glue", default=True, action="store_true", help="Glue rules can freely combine any X")
    optparser.add_option("", "--index", dest="sentindex", default=0, type="int", help="Sentence index")
    optparser.add_option("", "--skip-sents", dest="skip_sents", default=None, type="int", help="Skip sentences (usefel to resume decoding mid-way)")
    optparser.add_option("", "--sentperfile", dest="sent_per_file", default=500, type="int", help="Sentences per file")
    optparser.add_option("", "--fr-rule-terms", dest="fr_rule_terms", default=5, type="int", help="Terms in French side of Hiero rules")
    optparser.add_option("", "--fr-grule-terms", dest="fr_grule_terms", default=7,type="int", help="Terms in French side of Hiero glue rules") 
    optparser.add_option("", "--forcesent", dest="forceSent", type="string", help="target output sentence")
    optparser.add_option("", "--inputfile", dest="inFile", type="string", help="Input data file")
    optparser.add_option("", "--outputfile", dest="outFile", type="string", help="Output file")
    optparser.add_option("", "--glue-file", dest="glueFile", type="string", help="Glue rules file")
    optparser.add_option("", "--ttable-file", dest="ruleFile", type="string", help="SCFG rules file")
    optparser.add_option("", "--rm-file", dest="rmFile", type="string", help="phrase file for Lexicalized Reordering Model information")
    optparser.add_option("", "--lmodel-file", dest="lmFile", type="string", help="LM file")
    optparser.add_option("", "--use-srilm", dest="use_srilm", default=False, action="store_true", help="Flag for using SRILM")
    optparser.add_option("", "--no-lm-score", dest="no_lm_score", default=False, action="store_true", help="Don't compute lm score")
    optparser.add_option("", "--no-lm-state", dest="no_lm_state", default=False, action="store_true", help="Don't use LM state for KENLM")
    optparser.add_option("", "--no-lm-cache", dest="no_lm_cache", default=True, action="store_true", help="Don't cache LM queries")
    optparser.add_option("", "--no-dscnt-UNKlm", dest="no_dscnt_UNKlm", default=False, action="store_true", help="Don't discount LM penalty for UNK")
    optparser.add_option("", "--no-glue-penalty", dest="no_glue_penalty", default=False, action="store_true", help="Don't penalise glue rules")
    optparser.add_option("", "--tm-wgt-cnt", dest="tm_weight_cnt", default=5, type="int", help="# of TM weights")

    optparser.add_option("", "--trace-rules", dest="trace_rules", default=0, type="int", help="Trace the rules used in the k-best candidates as specified")
    optparser.add_option("", "--force-decode", dest="force_decode", default=False, action="store_true", help="Run the decoder in force decode mode")
    optparser.add_option("", "--reffile", dest="refFile", type="string", help="Reference file or prefix for multiple refs (for force decoding)")
    optparser.add_option("", "--tmg-wgt-cnt", dest="tmg_weight_cnt", default=4, type="int", help="# of TM weights for glue rules")
    optparser.add_option("", "--use-local", dest="local_path", default="None", type="string", help="Local path to copy the models")
    optparser.add_option("", "--nbest-extremum", dest="nbest_extremum", default=0, type="int", help="Produce nbest_extremum entries if provided; default full nbest list")

    optparser.add_option("", "--dw", dest="weight_d", default=0, type="float", help="distortion weight")
    optparser.add_option("", "--rw", dest="weight_r", default=0, type="float", help="weight for reordering rules")
    optparser.add_option("", "--dgw", dest="weight_dg", default=0, type="float", help="distortion weight for glue rules")
    optparser.add_option("", "--wd", dest="weight_w", default=0, type="float", help="width weight")
    optparser.add_option("", "--hd", dest="weight_h", default=0, type="float", help="hight weight")
    optparser.add_option("", "--dl", dest="beam-threshold", default=100, type="int", help="beam size for threshold pruning")
    optparser.add_option("", "--lm", dest="weight_lm", default=1.0, type="float", help="Language model weight")
    optparser.add_option("", "--tm", dest="weight_tm", type="string", help="Translation model weights as a string")
    optparser.add_option("", "--rm", dest="weight_rm", type="string", help="Reordering model weights as a string")
    optparser.add_option("", "--def-rm", dest="default_rm", type="string", help="Default values for reordering features as a string")
    optparser.add_option("", "--tmf", dest="weight_tmf", default=1.0, type="float", help="Forward trans model weight")
    optparser.add_option("", "--tmr", dest="weight_tmr", default=1.0, type="float", help="Reverse trans model weight")
    optparser.add_option("", "--lwf", dest="weight_lwf", default=0.5, type="float", help="Forward lexical trans weight")
    optparser.add_option("", "--lwr", dest="weight_lwr", default=0.5, type="float", help="Reverse lexical trans weight")
    optparser.add_option("", "--pp", dest="weight_pp", default=-1.0, type="float", help="Phrase penalty weight")
    optparser.add_option("", "--wp", dest="weight_wp", default=-2.0, type="float", help="Word penalty weight")
    optparser.add_option("", "--wg", dest="weight_glue", default=0.0, type="float", help="Glue rule weight")

    optparser.add_option("", "--cbp", dest="cbp", default=250, type="int", help="Cube pruning pop limit")
    optparser.add_option("", "--cbp-diversity", dest="cbp_diversity", default=0, type="int", help="Stack diversity in Cube pruning")
    optparser.add_option("", "--cbp-heap-diversity", dest="cbp_heap_diversity", default=0, type="int", help="Heap diversity in Cube pruning")
    optparser.add_option("", "--ttl", dest="ttl", default=20, type="int", help="# of translations for each source span")
    optparser.add_option("", "--ttlg", dest="ttlg", default=10, type="int", help="# of translations for each source span of glue rules")
    optparser.add_option("", "--btx", dest="beta_x", default=0.001, type="int", help="Beam threshold for X cells")
    optparser.add_option("", "--bts", dest="beta_s", default=0.001, type="int", help="Beam threshold for S cells")
    optparser.add_option("", "--eps", dest="eps", default=0.1, type="float", help="Beam search margin")

    optparser.add_option("", "--1b", dest="one_best", default=False, action="store_true", help="Just do the best derivation")
    optparser.add_option("", "--zmert-nbest", dest="zmert_nbest", default=False, action="store_true", help="N-best list should be in zmert format")
    optparser.add_option("", "--ng", dest="n_gram_size", default=5, type="int", help="n-gram size")

    optparser.add_option("", "--future-cost", dest="future_cost", default=0, type="int", help="type of future cost computation")
    optparser.add_option("", "--glue-type", dest="glue_type", default=0, type="int", help="type of glue rules")
    
    optparser.add_option("-v", "--verbose", dest="debug_level", type=int, default=0, help="verbose level")
    

    global opts, feat
    (opts, args) = optparser.parse_args()

    # Default flags & thresholds
    #opts.fr_rule_terms = 7
    #opts.fr_grule_terms = 9 # added 
    opts.max_span_size = 3  #added
    opts.unkPhrPenalty = -100.0 #added
    opts.max_phr_len = 10
    opts.nbest_limit = 100
    opts.use_unique_nbest = True
    opts.nbest_format = True
    opts.score_diff_threshold = 0.01
    #opts.elider = '*__*'
    opts.elider = ''

    if opts.configFile is None:
        sys.stderr.write('ERROR: Please specify a Config file. Exiting!!')
        sys.exit(1)
    if opts.configFile is not None:
        loadConfig()

    if opts.force_decode and not opts.refFile: 
        sys.stderr.write("ERROR: Forced decoding requires at least one reference file.\n")
        sys.stderr.write("       But, no reference file has been specified. Exiting!!\n\n")
        sys.exit(1)

    if (not opts.no_lm_state) and opts.use_srilm:
        sys.stderr.write("INFO: lm_state and srilm are mutually exclusive; no_lm_state can only be used with KENLM.\n")
        sys.stderr.write("      Setting no_lm_state to True and using SRILM\n")
        opts.no_lm_state = True

    sys.stderr.write( "INFO: Using the N-gram size      : %d\n" % (opts.n_gram_size) )
    sys.stderr.write( "INFO: Run decoder in 1NT mode    : %s\n" % (opts.one_nt_decode) )
    sys.stderr.write( "INFO: Use X freely in Glue rules : %s\n" % (opts.free_glue) )
    sys.stderr.write( "INFO: # of rule terms in Fr side : %d\n" % (opts.fr_rule_terms) )
    sys.stderr.write( "INFO: Generating unique N-best   : %s\n" % (opts.use_unique_nbest) )
    sys.stderr.write( "INFO: Computing LM score         : %s\n" % (not opts.no_lm_score) )
    sys.stderr.write( "INFO: Use state info for KENLM   : %s\n" % (not opts.no_lm_state) )
    sys.stderr.write( "INFO: Discount LM penalty 4 UNK  : %s\n" % (not opts.no_dscnt_UNKlm) )
    sys.stderr.write( "INFO: Glue rules penalty applied : %s\n" % (not opts.no_glue_penalty) )
    sys.stderr.write( "INFO: Cube pruning diversity     : %d\n" % (opts.cbp_diversity) )
    if opts.cbp_heap_diversity >0 :    sys.stderr.write( "INFO: Cube pruning heap diversity: %d\n" % (opts.cbp_heap_diversity) )
    if opts.future_cost >0 :    sys.stderr.write( "INFO: Future cost computation    : %d\n" % (opts.future_cost) )
    if opts.glue_type >0 :     sys.stderr.write( "INFO: glue rule type       : %d\n" % (opts.glue_type) )

    sys.stderr.write( "INFO: Force decoding status      : %s\n" % (opts.force_decode) )
    sys.stderr.write( "INFO: Reference file             : %s\n" % (opts.refFile) )

    if opts.nbest_extremum > 0:
        if opts.nbest_extremum * 2 >= opts.nbest_limit:
            opts.nbest_extremum = 20
            sys.stderr.write( "INFO: Nbest extremum must be less than half the nbest size. Using default nbest extremum of 20.\n" )
        else:
            sys.stderr.write( "INFO: Nbest extremum set: will produce top-%d and bottom-%d entries as nbest-list\n" % (opts.nbest_extremum, opts.nbest_extremum) )

    # Default weights for different features
    feat = Features()
    if opts.weight_tm:
        feat.tm = map( lambda x: float(x), opts.weight_tm.split(' ') )
    else:
        feat.tm = [opts.weight_tmf, opts.weight_tmr, opts.weight_lwf, \
                    opts.weight_lwr, opts.weight_pp]
    if opts.weight_rm:
        feat.rm = map( lambda x: float(x), opts.weight_rm.split(' ') )
        opts.rm_weight_cnt = len(feat.rm)
    elif opts.rm_weight_cnt > 0:
        feat.rm = [ 0.2 for i in range(opts.rm_weight_cnt) ]
    else:
        opts.rm_weight_cnt = 0
        feat.rm = None

    if opts.default_rm:
        opts.default_rm = map( lambda x: float(x), opts.default_rm.split(' ') )
        opts.default_rm = [opts.default_rm[:3], opts.default_rm[3:]]
    else:
        opts.default_rm = [(-1.5, -2.2, -0.3), (-1.5, -2.2, -0.3)]

    feat.wp = opts.weight_wp
    additionalFeat = [0.0, 0.0, 0.0, 0.0, 0.0, \
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0]      # lexicalized reordering model
    feat.d = opts.weight_d 
    feat.dg = opts.weight_dg 
    feat.r = opts.weight_r 
    feat.w = opts.weight_w
    feat.h = opts.weight_h 
     
    
    if len( feat.tm ) != int(opts.tm_weight_cnt):
        sys.stderr.write( "ERROR: # of TM features doesn't match with TM weights count! Exiting\n" )
        sys.exit(0)

    if feat.rm and len( feat.rm ) != opts.rm_weight_cnt:
        sys.stderr.write( "ERROR: # of RM features doesn't match with RM weights count! Exiting\n" )
        sys.exit(0)

    # Set the nbest_format to 'False' & nbest_limit to '1', if one_best option is set
    if opts.one_best:
        opts.nbest_format = False
        opts.nbest_limit = 1
        sys.stderr.write("INFO: one-best option specified. Option nbest-format will be turned off and nbest_limit set to 1.\n")
    sys.stderr.write( "INFO: cbp/ Nbest limit : %d/ %d\n" % (opts.cbp, opts.nbest_limit) )

    if opts.shallow_hiero: sys.stderr.write( "INFO: Shallow decoding hiero with order : %d...\n" % (opts.sh_order) )
    else: sys.stderr.write( "INFO: Shallow decoding hiero turned off; decoding as full hiero ...\n" )

    if opts.use_srilm: sys.stderr.write( "INFO: Using SRILM language model wrapper ...\n" )
    else: sys.stderr.write( "INFO: Using KenLM language model wrapper ...\n" )

    feat.lm = opts.weight_lm
    feat.glue = opts.weight_glue

    opts.lm_index = 6
    opts.word_penalty = 5
    opts.glue_penalty = 7 
    # Initialize feature vector for Unknown words
    if opts.no_dscnt_UNKlm:
        unk_featLst = [-13.8155, -13.8155, -13.8155, -13.8155, 0.99989631572895199, -1, 0.0, 0.0]+additionalFeat  # unk rule prob (for unknown words)
    else:
        unk_featLst = [-13.8155, -13.8155, -13.8155, -13.8155, 0.99989631572895199, -1, -100.0, 0.0]+additionalFeat  # unk rule prob (for unknown words)
    (lm_score, p_score) = getScores(unk_featLst)
    lm_score = lm_score/0.434294
    opts.U_lpTup = (p_score, lm_score, unk_featLst)

    if opts.local_path is not 'None':
        sys.stderr.write( "About to copy language model locally ...\n" )
        copyModels()


def getScores(fLst):
    '''Get the score given the feat vector'''
    global feat

    lm_score = feat.lm * fLst[6]
    p_score = (feat.tm[0] * fLst[0]) + (feat.tm[1] * fLst[1]) + (feat.tm[2] * fLst[2]) + \
                (feat.tm[3] * fLst[3]) + (feat.tm[4] * fLst[4]) + (feat.wp * fLst[5]) + \
                (feat.glue * fLst[7])
    additionCost = 0
    index = 8
    additionCost += feat.d * fLst[index]
    additionCost += feat.r * fLst[index+1]
    additionCost += feat.dg * fLst[index+2]
    additionCost += feat.w * fLst[index+3]
    additionCost += feat.h * fLst[index+4]
         
    p_score += additionCost
    return (lm_score, p_score)


def loadConfig():
    '''Load the configuration file'''

    global opts
    parameter_line = ''
    tmLst = []
    rmLst = []
    rmDefLst = []
    line_cnt = 0
    opts.rm_weight_cnt = 0
    cF = open(opts.configFile, 'r')
    for line in cF:
        line = line.strip()
        line_cnt += 1
        if line.startswith('#') or line == '':
            parameter_line = ''
            continue

        if line.startswith('['):
            parameter_line = line
            continue

        if len(parameter_line) > 0:
            if parameter_line == "[hiero-options]":
                if line.find("=") <= 0:
                    sys.stderr.write("Line # %d in file %s : %s\n" % (line_cnt, opts.configFile, line))
                    sys.stderr.write("Unknown hiero option specified. Exiting!!\n")
                    sys.exit(1)

                (feat, val) = line.split("=")
                feat = feat.strip()
                if feat == "fr-rule-terms": opts.fr_rule_terms = int(val)
                elif feat == "cbp": opts.cbp = int(val)
                elif feat == "cbp-diversity": opts.cbp_diversity = int(val)
                elif feat == "cbp-heap-diversity": opts.cbp_heap_diversity = int(val)
                elif feat == "future-cost": opts.future_cost = int(val)
                elif feat == "glue-type": opts.glue_type = int(val)
                elif feat == "shallow-order": opts.sh_order = int(val)
                else:
                    val = val.strip().lower()
                    if val == 'true':
                        if feat == "shallow-hiero": opts.shallow_hiero = True
                        elif feat == "one-nt-decode": opts.one_nt_decode = True
                        elif feat == "free-glue": opts.free_glue = True
                        elif feat == "use-srilm": opts.use_srilm = True
                        elif feat == "no-glue-penalty": opts.no_glue_penalty = True
                        elif feat == "no-lm-score": opts.no_lm_score = True
                        elif feat == "no-dscnt-UNKlm": opts.no_dscnt_UNKlm = True
                    elif val == 'false':
                        if feat == "free-glue": opts.free_glue = False
            elif parameter_line == "[sentperfile]": opts.sent_per_file = int(line)
            elif parameter_line == "[inputfile]": opts.inFile = line
            elif parameter_line == "[outputfile]": opts.outFile = line
            elif parameter_line == "[glue-file]" and not opts.glueFile: opts.glueFile = line
            elif parameter_line == "[ttable-file]":
                opts.tm_weight_cnt, ttable_file = line.split(' ')
                opts.tm_weight_cnt = int( opts.tm_weight_cnt )
                # do not override ruleFile if it is specified in cmd line
                if not opts.ruleFile: opts.ruleFile = ttable_file
            elif parameter_line == "[distortion-file]":
                opts.rm_weight_cnt, rmtable_file = line.split(' ')
                opts.rm_weight_cnt = int( opts.rm_weight_cnt )
                # do not override reorderingFile if it is specified in cmd line
                if not opts.rmFile: opts.rmFile = rmtable_file
            elif parameter_line == "[weight_d]": opts.weight_d = float(line)
            elif parameter_line == "[weight_r]": opts.weight_r = float(line)
            elif parameter_line == "[weight_dg]": opts.weight_dg = float(line)
            elif parameter_line == "[weight_wd]": opts.weight_w = float(line)
            elif parameter_line == "[weight_hd]": opts.weight_h = float(line)
            elif parameter_line == "[distortion-limit]": 
                opts.dist_limit = int(line)
                if opts.dist_limit <= 0: opts.dist_limit = 10000
            elif parameter_line == "[ttable-limit]": opts.ttl = int(line)
            elif parameter_line == "[glue-ttable-limit]": opts.ttlg = int(line)
            elif parameter_line == "[lmodel-file]":
                opts.n_gram_size, lm_file = line.split(' ')
                opts.n_gram_size = int( opts.n_gram_size )
                if not opts.lmFile: opts.lmFile = lm_file
            elif parameter_line == "[weight_wp]": opts.weight_wp = float( line )
            elif parameter_line == "[weight_glue]": opts.weight_glue = float( line )
            elif parameter_line == "[weight_lm]":
                opts.weight_lm = float( line )
            elif parameter_line == "[n-best-list]":
                if line.find("=") <= 0:
                    if line.isdigit():
                        opts.nbest_limit = int( line )     # for backward compatibility
                        continue
                    else:
                        sys.stderr.write("Line # %d in file %s : %s\n" % (line_cnt, opts.configFile, line))
                        sys.stderr.write("Unknown n-best-list option specified. Exiting!!\n")
                        sys.exit(1)

                (feat, val) = line.split("=")
                feat = feat.strip()
                val = val.strip().lower()
                if feat == "nbest-size": opts.nbest_limit = int( val )
                elif val == 'true':
                    if feat == "nbest-format" or feat == "nbest_format": opts.nbest_format = True
                    elif feat == "one-best" or feat == "one_best": opts.one_best = True
                elif val == 'false':
                    if feat == "use-unique-nbest" or feat == "use_unique_nbest": opts.use_unique_nbest = False
                    elif feat == "nbest-format" or feat == "nbest_format": opts.nbest_format = False
                    elif feat == "one-best" or feat == "one_best": opts.one_best = False
            elif parameter_line == "[weight_tm]":
                tmLst.append( line )
            elif parameter_line == "[weight_rm]":
                rmLst.append( line )
            elif parameter_line == "[lrm-default]":
                rmDefLst.append( line )

    cF.close()
    if tmLst:
        opts.weight_tm = ' '.join( tmLst )
    if rmLst:
        opts.weight_rm = ' '.join( rmLst )
    if rmDefLst:
        opts.default_rm = ' '.join( rmDefLst )

def copyModels():
    """ Copies the model files to the local path.
        Specifically the translation and language models are copied.
    """

    # Create the local path if it doesn't exist
    createPath(opts.local_path)
    if not opts.local_path.endswith('/'): opts.local_path = opts.local_path + '/'

    sys.stdout.write("Copying the model files to the local path: %s ...\n\n" % (opts.local_path))

    """
    # Copy the phrase table - racing not possible
    (ptable_path, ptable) = os.path.split(opts.ruleFile)
    local_path = opts.local_path + os.path.basename(ptable_path)
    createPath(local_path)
    local_ptable = local_path + '/' + ptable
    if not os.path.exists(local_ptable) or not sameSize(opts.ruleFile, local_ptable):
        copyFile(opts.ruleFile, local_ptable, False)
    """

    # Copy the language model - race condition possible
    (lmodel_path, lmodel) = os.path.split(opts.lmFile)
    local_lmodel = opts.local_path + lmodel
    if not os.path.exists(local_lmodel) or not sameSize(opts.lmFile, local_lmodel):
        copyFile(opts.lmFile, local_lmodel, True)

    # Point the models to the local copies
    #opts.ruleFile = local_ptable
    opts.lmFile = local_lmodel

def createPath(l_path):
    # if multiple decoder instances are scheduled on the same machine,
    # we need to avoid race conditions where different instances attempt to
    # create the same directory or copy the same file.
    # Make them sleep for a while to avoid race conditions.
    time.sleep( random.randint(5, 45) )

    if not os.path.exists(l_path):
        os.makedirs(l_path)

def sameSize(src_file, dst_file):

    return os.path.getsize(src_file) == os.path.getsize(dst_file)

def copyFile(src_file, dst_file, race_flag):
    """ Routine for copying the source file src_file to destination.
        It additionally ensures that the copied file is of the same size as original
        ensuring correctness.
        Additionally, if the race_flag is set to True - indicating that multiple instances
        might try to copy the same file, it avoids race condition by allowing only one
        instance to create the copy while putting others to sleep.
    """

    if race_flag:
        time.sleep( random.randint(5, random.randint(10, 50)) )
        if os.path.exists(dst_file):
            while not sameSize(src_file, dst_file):
                time.sleep(10)
            return None

    while(True):
        shutil.copy(src_file, dst_file)
        if sameSize(src_file, dst_file):
            break
