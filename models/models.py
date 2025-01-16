# models.py

class clsMouvementcomptable:
    def __init__(self, SO_CODESOCIETE, FE_CODEFRAISENVOI, TR_CODETRANSFERT, EC_CODEEFFETCHEQUE, CR_CODECREDIT, IM_CODEBIENIMMOBILISE, OV_CODEORDREVIREMENT,
                 BU_CODEBUDGET, RS_NUMREGLEMENT, MS_NUMPIECE, AG_CODEAGENCE, PV_CODEPOINTVENTE, MC_DATEPIECE, MC_NUMPIECE, NUMEROBORDEREAU, MC_NUMSEQUENCE,
                 MR_CODEMODEREGLEMENT, JO_CODEJOURNAL, TI_IDTIERS, MI_CODEMISE, ST_STICKERCODE1, ST_STICKERCODE2, STICKER, CO_CODECOMPTE1, CO_CODECOMPTE2,
                 PL_CODENUMCOMPTE, PL_NUMCOMPTE, MC_REFERENCEPIECE, MC_LIBELLEOPERATION, PI_CODEPIECE, MC_NUMPIECETIERS, MC_NOMTIERS, TS_CODETYPESCHEMACOMPTABLE,
                 MC_SENSBILLETAGE, MC_MONTANTDEBIT, MC_MONTANTCREDIT, MC_ANNULATION, OP_CODEOPERATEUR, SL_LIBELLEECRAN, SL_LIBELLEMOUCHARD, TYPEOPERATION,
                 LG_CODELANGUE, clsObjetEnvoi, clsCoupure):
        self.SO_CODESOCIETE = SO_CODESOCIETE
        self.FE_CODEFRAISENVOI = FE_CODEFRAISENVOI
        self.TR_CODETRANSFERT = TR_CODETRANSFERT
        self.EC_CODEEFFETCHEQUE = EC_CODEEFFETCHEQUE
        self.CR_CODECREDIT = CR_CODECREDIT
        self.IM_CODEBIENIMMOBILISE = IM_CODEBIENIMMOBILISE
        self.OV_CODEORDREVIREMENT = OV_CODEORDREVIREMENT
        self.BU_CODEBUDGET = BU_CODEBUDGET
        self.RS_NUMREGLEMENT = RS_NUMREGLEMENT
        self.MS_NUMPIECE = MS_NUMPIECE
        self.AG_CODEAGENCE = AG_CODEAGENCE
        self.PV_CODEPOINTVENTE = PV_CODEPOINTVENTE
        self.MC_DATEPIECE = MC_DATEPIECE
        self.MC_NUMPIECE = MC_NUMPIECE
        self.NUMEROBORDEREAU = NUMEROBORDEREAU
        self.MC_NUMSEQUENCE = MC_NUMSEQUENCE
        self.MR_CODEMODEREGLEMENT = MR_CODEMODEREGLEMENT
        self.JO_CODEJOURNAL = JO_CODEJOURNAL
        self.TI_IDTIERS = TI_IDTIERS
        self.MI_CODEMISE = MI_CODEMISE
        self.ST_STICKERCODE1 = ST_STICKERCODE1
        self.ST_STICKERCODE2 = ST_STICKERCODE2
        self.STICKER = STICKER
        self.CO_CODECOMPTE1 = CO_CODECOMPTE1
        self.CO_CODECOMPTE2 = CO_CODECOMPTE2
        self.PL_CODENUMCOMPTE = PL_CODENUMCOMPTE
        self.PL_NUMCOMPTE = PL_NUMCOMPTE
        self.MC_REFERENCEPIECE = MC_REFERENCEPIECE
        self.MC_LIBELLEOPERATION = MC_LIBELLEOPERATION
        self.PI_CODEPIECE = PI_CODEPIECE
        self.MC_NUMPIECETIERS = MC_NUMPIECETIERS
        self.MC_NOMTIERS = MC_NOMTIERS
        self.TS_CODETYPESCHEMACOMPTABLE = TS_CODETYPESCHEMACOMPTABLE
        self.MC_SENSBILLETAGE = MC_SENSBILLETAGE
        self.MC_MONTANTDEBIT = MC_MONTANTDEBIT
        self.MC_MONTANTCREDIT = MC_MONTANTCREDIT
        self.MC_ANNULATION = MC_ANNULATION
        self.OP_CODEOPERATEUR = OP_CODEOPERATEUR
        self.SL_LIBELLEECRAN = SL_LIBELLEECRAN
        self.SL_LIBELLEMOUCHARD = SL_LIBELLEMOUCHARD
        self.TYPEOPERATION = TYPEOPERATION
        self.LG_CODELANGUE = LG_CODELANGUE
        self.clsObjetEnvoi = clsObjetEnvoi
        self.clsCoupure = clsCoupure
        

class clsObjetEnvoi:
    def __init__(self, OE_A, OE_Y, OE_J,OE_U,OE_G,OE_T):
        self.OE_A = OE_A
        self.OE_Y = OE_Y
        self.OE_J = OE_J
        self.OE_U = OE_U
        self.OE_G = OE_G
        self.OE_T = OE_T

class clsCoupure:
    def __init__(self, CB_CODE, CB_LIBELLE, CB_VALEUR, CB_STATUT, SL_LIBELLEECRAN, SL_LIBELLEMOUCHARD, TYPEOPERATION, LG_CODELANGUE, clsObjetEnvoi):
        self.CB_CODE = CB_CODE
        self.CB_LIBELLE = CB_LIBELLE
        self.CB_VALEUR = CB_VALEUR
        self.CB_STATUT = CB_STATUT
        self.SL_LIBELLEECRAN = SL_LIBELLEECRAN
        self.SL_LIBELLEMOUCHARD = SL_LIBELLEMOUCHARD
        self.TYPEOPERATION = TYPEOPERATION
        self.LG_CODELANGUE = LG_CODELANGUE
        self.clsObjetEnvoi = clsObjetEnvoi


class clsBilletage:
    def __init__(self, AG_CODEAGENCE, BI_NUMPIECE, BI_NUMSEQUENCE, BI_QUANTITEENTREE, BI_QUANTITESORTIE, CB_CODECOUPURE, MC_DATEPIECE, MC_NUMPIECE, MC_NUMSEQUENCE,PL_CODENUMCOMPTE,TYPEOPERATION):
        self.AG_CODEAGENCE = AG_CODEAGENCE
        self.BI_NUMPIECE = BI_NUMPIECE
        self.BI_NUMSEQUENCE = BI_NUMSEQUENCE
        self.BI_NUMSEQUENCE = BI_NUMSEQUENCE
        self.BI_QUANTITEENTREE = BI_QUANTITEENTREE
        self.BI_QUANTITESORTIE = BI_QUANTITESORTIE
        self.CB_CODECOUPURE = CB_CODECOUPURE
        self.MC_DATEPIECE = MC_DATEPIECE
        self.MC_NUMPIECE = MC_NUMPIECE
        self.MC_NUMSEQUENCE = MC_NUMSEQUENCE
        self.PL_CODENUMCOMPTE = PL_CODENUMCOMPTE
        self.TYPEOPERATION = TYPEOPERATION

class clsEtatmouvementacomptabilisers:
    def __init__(self, AG_CODEAGENCE, CO_CODECOMPTE, EM_DATEPIECE, EM_LIBELLEOPERATION, EM_MONTANT, EM_NOMOBJET, EM_NUMEROSEQUENCE, EM_NUMPIECETIERS, EM_REFERENCEPIECE,EM_SCHEMACOMPTABLECODE,EM_SENSBILLETAGE,MB_IDTIERS,OP_CODEOPERATEUR,PI_CODEPIECE,PL_CODENUMCOMPTE,PV_CODEPOINTVENTE,SC_LIGNECACHEE,TS_CODETYPESCHEMACOMPTABLE):
        self.AG_CODEAGENCE = AG_CODEAGENCE
        self.CO_CODECOMPTE = CO_CODECOMPTE
        self.EM_DATEPIECE = EM_DATEPIECE
        self.EM_LIBELLEOPERATION = EM_LIBELLEOPERATION
        self.EM_MONTANT = EM_MONTANT
        self.EM_NOMOBJET = EM_NOMOBJET
        self.EM_NUMEROSEQUENCE = EM_NUMEROSEQUENCE
        self.EM_NUMPIECETIERS = EM_NUMPIECETIERS
        self.EM_REFERENCEPIECE = EM_REFERENCEPIECE
        self.EM_SCHEMACOMPTABLECODE = EM_SCHEMACOMPTABLECODE
        self.EM_SENSBILLETAGE = EM_SENSBILLETAGE
        self.MB_IDTIERS = MB_IDTIERS
        self.OP_CODEOPERATEUR = OP_CODEOPERATEUR
        self.PI_CODEPIECE = PI_CODEPIECE
        self.PL_CODENUMCOMPTE = PL_CODENUMCOMPTE
        self.PV_CODEPOINTVENTE = PV_CODEPOINTVENTE
        self.SC_LIGNECACHEE = SC_LIGNECACHEE
        self.TS_CODETYPESCHEMACOMPTABLE = TS_CODETYPESCHEMACOMPTABLE
        
        