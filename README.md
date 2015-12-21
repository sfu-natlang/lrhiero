lrhiero
========

This is the decoder of left-to-right hierarchical phrase-based (lrhiero) SMT system.


# Usage
```
python decoder_cp.py --config <lrhiero.ini> --inputfile <test.in> --outputfile <test.out> --ttable-file <test.rule> --1b
```

Use the ```--help``` or ```-h``` to see other options.

# Requirements
* Python 2.6 or higher
* SRILM For building language model (LM)
* KenLM Library for querying the language model (a Python wrapper is included with the decoder and the source for the wrapper will be released soon)

# Advance Features of the Decoder

## Grammar
LR-Hiero uses a spesific form of SCFG (Synchronous Context-Free Grammar) rules which are prefix-lexicalized or in so-called Greibach Normal Form (GNF) on target side.


### File Format
The content of rule file is for each line: source phrase, target phrase, and features. 
```
aber X__1 sagen X__2 ||| but say X__1 X__2 ||| -0.558224 -0.000100005 -1.14023 -1.84913
```

## Incremental Decoding
LR-Hiero decoder can produce the transaltion incrementally given the input sentence word by word. The decoder needs a segmenter which indicates where it is safe for the decoder to emit the translation. In current version, the decoder gets the segmentation inofrmation in a file in parallel to the input sentence.

```
python decoder_cp.py --config <lrhiero.ini> --inputfile <test.in> --outputfile <test.out> --ttable-file <test.rule> --inc-decode --segfile <test.seg> --1b
```

NOTE: the incremental is just used for test phase (not generating n-best list for tuning phase).

## Handling Unknown Words
Unknown words are copied verbatim to the output. For each unknown word/phrase 4 glue rules are generated and added to the grammar, therefore they may be placed out of order in the output. Unknown words are also scored by the language model. 

<!--- TODO: add -drop-unknown switch to the decoder
Alternatively, you may want to drop unknown words. To do so add the switch -drop-unknown.

When translating between languages that use different writing sentences (say, Chinese-English), dropping unknown words results in better BLEU scores. However, it is misleading to a human reader, and it is unclear what the effect on human judgment is. 
-->
<!--
## Verbose
Switch -verbose (short -v) displays additional run time information.
-->

# Citation
If you use this decoder in you research, consider citing:
* Efficient Left-to-Right Hierarchical Phrase-based Translation with Improved Reordering. Maryam Siahbani, Baskaran Sankaran and Anoop Sarkar. In Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP 2013). Oct 18-21, 2013. Seattle, USA.
* Incremental Translation using a Hierarchical Phrase-based Translation System. Maryam Siahbani, Ramtin M. Seraj, Baskaran Sankaran and Anoop Sarkar. In Proceedings of the 2014 IEEE Spoken Language Technology Workshop (SLT 2014). December 7-10, 2014. Nevada, USA.


# Contacts

Maryam Siahbani, Anoop Sarkar

{msiahban,anoop}@sfu.ca

NatLang Lab, School of Computing Science
Simon Fraser University, 
Burnaby, BC V5A 1S6. Canada
