# Extracto de HL7 v2.5 para el verificador

> **Copia pública.** El original del laboratorio es un encargo de la fase 13 que lleva el capítulo 2 de HL7 v2.5 entero y
> extractos del 3. Ese texto es de Health Level Seven International y no se reproduce sin su permiso, así que aquí solo
> quedan, tal cual y sin los pies de página, las filas de las tres tablas que lee `acuse_referencia._tabla`: 0003, 0004 y
> 0211. No es obra del autor ni está cubierto por las licencias de este repositorio. El estándar completo se obtiene de
> HL7 (hl7.org), con su licencia.
>
> La huella del juez publicado difiere de la del laboratorio solo por este fichero (`verificador/MANIFIESTO.txt`).

                                                 HL7 Table 0003 - Event type
      Value        Description                                                             Comment
       A01         ADT/ACK - Admit/visit notification
       A02         ADT/ACK - Transfer a patient
       A03         ADT/ACK - Discharge/end visit
       A04         ADT/ACK - Register a patient
       A05         ADT/ACK - Pre-admit a patient
       A06         ADT/ACK - Change an outpatient to an inpatient
       A07         ADT/ACK - Change an inpatient to an outpatient
       A08         ADT/ACK - Update patient information
       A09         ADT/ACK - Patient departing - tracking
       A10         ADT/ACK - Patient arriving - tracking
       A11         ADT/ACK - Cancel admit/visit notification
       A12         ADT/ACK - Cancel transfer
       A13         ADT/ACK - Cancel discharge/end visit
       A14         ADT/ACK - Pending admit
       A15         ADT/ACK - Pending transfer
       A16         ADT/ACK - Pending discharge
       A17         ADT/ACK - Swap patients
       A18         ADT/ACK - Merge patient information (for backward compatibility only)




     Value   Description                                                                           Comment
      A19    QRY/ADR - Patient query
      A20    ADT/ACK - Bed status update
      A21    ADT/ACK - Patient goes on a “leave of absence”
      A22    ADT/ACK - Patient returns from a “leave of absence”
      A23    ADT/ACK - Delete a patient record
      A24    ADT/ACK - Link patient information
      A25    ADT/ACK - Cancel pending discharge
      A26    ADT/ACK - Cancel pending transfer
      A27    ADT/ACK - Cancel pending admit
      A28    ADT/ACK - Add person information
      A29    ADT/ACK - Delete person information
      A30    ADT/ACK - Merge person information (for backward compatibility only)
      A31    ADT/ACK - Update person information
      A32    ADT/ACK - Cancel patient arriving - tracking
      A33    ADT/ACK - Cancel patient departing - tracking
      A34    ADT/ACK - Merge patient information - patient ID only (for backward
             compatibility only)
      A35    ADT/ACK - Merge patient information - account number only (for backward
             compatibility only)
      A36    ADT/ACK - Merge patient information - patient ID and account number (for
             backward compatibility only)
      A37    ADT/ACK - Unlink patient information
      A38    ADT/ACK - Cancel pre-admit
      A39    ADT/ACK - Merge person – patient ID (for backward compatibility only)
      A40    ADT/ACK - Merge patient – patient identifier list
      A41    ADT/ACK - Merge account - patient account number
      A42    ADT/ACK - Merge visit - visit number
      A43    ADT/ACK - Move patient information – patient identifier list
      A44    ADT/ACK - Move account information - patient account number
      A45    ADT/ACK - Move visit information - visit number
      A46    ADT/ACK - Change patient ID (for backward compatibility only)
      A47    ADT/ACK - Change patient identifier list
      A48    ADT/ACK - Change alternate patient ID (for backward compatibility only)
      A49    ADT/ACK - Change patient account number
      A50    ADT/ACK - Change visit number
      A51    ADT/ACK - Change alternate visit ID
      A52    ADT/ACK – Cancel leave of absence for a patient
      A53    ADT/ACK – Cancel patient returns from a leave of absence
      A54    ADT/ACK - Change attending doctor
      A55    ADT/ACK – Cancel change attending doctor
      A60    ADT/ACK – Update allergy information
      A61    ADT/ACK – Change consulting doctor
      A62    ADT/ACK – Cancel change consulting doctor
      B01    PMU/ACK – Add personnel record
      B02    PMU/ACK – Update personnel record
      B03    PMU/ACK – Delete personnel re cord
      B04    PMU/ACK – Active practicing person
      B05    PMU/ACK – Deactivate practicing person
      B06    PMU/ACK – Terminate practicing person
      B07    PMU/ACK – Grant Certificate/Permission
      B08    PMU/ACK – Revoke Certificate/Permission
      C01    CRM - Register a patient on a clinical trial
      C02    CRM - Cancel a patient registration on clinical trial (for clerical mistakes only)



      Value       Description                                                                  Comment
       C03        CRM - Correct/update registration information
       C04        CRM - Patient has gone off a clinical trial
       C05        CRM - Patient enters phase of clinical trial
       C06        CRM - Cancel patient entering a phase (clerical mistake)
       C07        CRM - Correct/update phase information
       C08        CRM - Patient has gone off phase of clinical trial
       C09        CSU - Automated time intervals for reporting, like monthly
       C10        CSU - Patient completes the clinical trial
       C11        CSU - Patient completes a phase of the clinical trial
       C12        CSU - Update/correction of patient order/result information
      CNQ         Cancel Query
       I01        RQI/RPI - Request for insurance information
       I02        RQI/RPL - Request/receipt of patient selection display list
       I03        RQI/RPR - Request/receipt of patient selection list
       I04        RQD/RPI - Request for patient demographic data
       I05        RQC/RCI - Request for patient clinical information
       I06        RQC/RCL - Request/receipt of clinical data listing
       I07        PIN/ACK - Unsolicited insurance information
       I08        RQA/RPA - Request for treatment authorization information
       I09        RQA/RPA - Request for modification to an authorization
       I10        RQA/RPA - Request for resubmission of an authorization
       I11        RQA/RPA - Request for cancellation of an authorization
       I12        REF/RRI - Patient referral
       I13        REF/RRI - Modify patient referral
       I14        REF/RRI - Cancel patient referral
       I15        REF/RRI - Request patient referral status
       J01        QCN/ACK – Cancel query/acknowledge message
       J02        QSX/ACK – Cancel subscription/acknowledge message
       K11        RSP - Segment pattern response in response to QBP^Q11
       K13        RTB - Tabular response in response to QBP^Q13
       K15        RDY - Display response in response to QBP^Q15
       K21        RSP – Get person demographics response
       K22        RSP – Find candidates response
       K23        RSP – Get corresponding identifiers response
       K24        RSP – Allocate identifiers response
       K25        RSP - Personnel Information by Segment Response
       M01        MFN/MFK - Master file not otherwise specified (for backward compatibility
                  only)
      M02         MFN/MFK - Master file – staff practitioner
      M03         MFN/MFK - Master file - test/observation (for backward compatibility only)
      M04         MFN/MFK - Master files charge description
      M05         MFN/MFK - Patient location master file
      M06         MFN/MFK - Clinical study with phases and schedules master file
      M07         MFN/MFK - Clinical study without phases but with schedules master file
      M08         MFN/MFK - Test/observation (numeric) master file
      M09         MFN/MFK - Test/observation (categorical) master file
      M10         MFN/MFK - Test /observation batteries master file
      M11         MFN/MFK - Test/calculated observations master file
      M12         MFN/MFK – Master file notification message
      M13         MFN/MFK - Master file notification - general
      M14         MFN/MFK - Master file notification – site defined
      M15         MFN/MFK – Inventory item master file notification




     Value   Description                                                                      Comment
      N01    NMQ/NMR - Application management query message
      N02    NMD/ACK - Application management data message (unsolicited)
      O01    ORM - Order message (also RDE, RDS, RGV, RAS)
      O02    ORR - Order response (also RRE, RRD, RRG, RRA)
      O03    OMD – Diet order
      O04    ORD – Diet order acknowledgment
      O05    OMS – Stock requisition order
      O06    ORS – Stock requisition acknowledgment
      O07    OMN – Non-stock requisition order
      O08    ORN – Non-stock requisition acknowledgment
      O09    OMP – Pharmacy/treatment order
      O10    ORP – Pharmacy/treatment order acknowledgment
      O11    RDE – Pharmacy/treatment encoded order
      O12    RRE – Pharmacy/treatment encoded order acknowledgment
      O13    RDS – Pharmacy/treatment dispense
      O14    RRD – Pharmacy/treatment dispense acknowledgment
      O15    RGV – Pharmacy/treatment give
      O16    RRG – Pharmacy/treatment give acknowledgment
      O17    RAS – Pharmacy/treatment administration
      O18    RRA – Pharmacy/treatment administration acknowledgment
      O19    OMG – General clinical order
      O20    ORG/ORL – General clinical order response
      O21    OML - Laboratory order
      O22    ORL - General laboratory order response message to any OML
      O23    OMI – Imaging order
      O24    ORI – Imaging order response message to any OMI
      O25    RDE - Pharmacy/treatment refill authorization request
      O26    RRE - Pharmacy/Treatment Refill Authorization Acknowledgement
      O27    OMB – Blood product order
      O28    ORB – Blood product order acknowledgment
      O29    BPS – Blood product dispense status
      O30    BRP – Blood product dispense status acknowledgment
      O31    BTS – Blood product transfusion/disposition
      O32    BRT – Blood product transfusion/disposition acknowledgment
      O33    OML – Laboratory order for multiple orders related to a single specimen
      O34    ORL – Laboratory order response message to a multiple order related to single
             specimen OML
      O35    OML – Laboratory order for multiple orders related to a single container of a
             specimen
      O36    ORL - Laboratory order response message to a single container of a specimen
             OML
      P01    BAR/ACK - Add patient accounts
      P02    BAR/ACK - Purge patient accounts
      P03    DFT/ACK - Post detail financial transaction
      P04    QRY/DSP – Generate bill and A/R statements
      P05    BAR/ACK – Update account
      P06    BAR/ACK - End account
      P07    PEX - Unsolicited initial individual product experience report
      P08    PEX - Unsolicited update individual product experience report
      P09    SUR - Summary product experience report
      P10    BAR/ACK –Transmit Ambulatory Payment Classification(APC)
      P11    DFT/ACK - Post Detail Financial Transactions - New
      P12    BAR/ACK - Update Diagnosis/Procedure



      Value       Description                                                           Comment
       PC1        PPR - PC/ problem add
       PC2        PPR - PC/ problem update
       PC3        PPR - PC/ problem delete
       PC4        QRY - PC/ problem query
       PC5        PRR - PC/ problem response
       PC6        PGL - PC/ goal add
       PC7        PGL - PC/ goal update
       PC8        PGL - PC/ goal delete
       PC9        QRY - PC/ goal query
      PCA         PPV - PC/ goal response
      PCB         PPP - PC/ pathway (problem-oriented) add
      PCC         PPP - PC/ pathway (problem-oriented) update
      PCD         PPP - PC/ pathway (problem-oriented) delete
      PCE         QRY - PC/ pathway (problem-oriented) query
       PCF        PTR - PC/ pathway (problem-oriented) query response
      PCG         PPG - PC/ pathway (goal-oriented) add
      PCH         PPG - PC/ pathway (goal-oriented) update
       PCJ        PPG - PC/ pathway (goal-oriented) delete
      PCK         QRY - PC/ pathway (goal-oriented) query
       PCL        PPT - PC/ pathway (goal-oriented) query response
       Q01        QRY/DSR - Query sent for immediate response
       Q02        QRY/QCK - Query sent for deferred response
       Q03        DSR/ACK - Deferred response to a query
       Q04        EQQ – Embedded query language query
       Q05        UDM/ACK - Unsolicited display update message
       Q06        OSQ/OSR - Query for order status
       Q07        VQQ – Virtual table query
       Q08        SPQ – Stored procedure request
       Q09        RQQ – event replay query
       Q11        QBP - Query by parameter requesting an RSP segment pattern response
       Q13        QBP - Query by parameter requesting an RTB - tabular response
       Q15        QBP - Query by parameter requesting an RDY display response
       Q16        QSB – Create subscription
       Q17        QVR – Query for previous events
       Q21        QBP – Get person demographics
       Q22        QBP – Find candidates
       Q23        QBP – Get corresponding identifiers
       Q24        QBP – Allocate identifiers
       Q25        QBP - Personnel Information by Segment Query
       Q26        ROR - Pharmacy/treatment order response
       Q27        RAR - Pharmacy/treatment administration information
       Q28        RDR - Pharmacy/treatment dispense information
       Q29        RER - Pharmacy/treatment encoded order information
       Q30        RGR - Pharmacy/treatment dose information
       R01        ORU/ACK - Unsolicited transmission of an observation message
       R02        QRY - Query for results of observation
       R03        QRY/DSR Display-oriented results, query/unsol. update (for backward
                  compatibility only) (Replaced by Q05)
      R04         ORF - Response to query; transmission of requested observation
      ROR         ROR - Pharmacy prescription order query response
      R07         EDR - Enhanced Display Response
      R08         TBR - Tabular Data Response




     Value   Description                                                                     Comment
      R09    ERP - Event Replay Response
      R21    OUL – Unsolicited laboratory observation
      R22    OUL – Unsolicited Specimen Oriented Observation Message
      R23    OUL – Unsolicited Specimen Container Oriented Observation Message
      R24    OUL – Unsolicited Order Oriented Observation Message
      R30    ORU – Unsolicited Point-Of-Care Observation Message Without Existing Order
             – Place An Order
      R31    ORU – Unsolicited New Point-Of-Care Observation Message – Search For An
             Order
      R32    ORU – Unsolicited Pre-Ordered Point-Of-Care Observation
      S01    SRM/SRR - Request new appointment booking
      S02    SRM/SRR - Request appointment rescheduling
      S03    SRM/SRR - Request appointment modification
      S04    SRM/SRR - Request appointment cancellation
      S05    SRM/SRR - Request appointment discontinuation
      S06    SRM/SRR - Request appointment deletion
      S07    SRM/SRR - Request addition of service/resource on appointment
      S08    SRM/SRR - Request modification of service/resource on appointment
      S09    SRM/SRR - Request cancellation of service/resource on appointment
      S10    SRM/SRR - Request discontinuation of service/resource on appointment
      S11    SRM/SRR - Request deletion of service/resource on appointment
      S12    SIU/ACK - Notification of new appointment booking
      S13    SIU/ACK - Notification of appointment rescheduling
      S14    SIU/ACK - Notification of appointment modification
      S15    SIU/ACK - Notification of appointment cancellation
      S16    SIU/ACK - Notification of appointment discontinuation
      S17    SIU/ACK - Notification of appointment deletion
      S18    SIU/ACK - Notification of addition of service/resource on appointment
      S19    SIU/ACK - Notification of modification of service/resource on appointment
      S20    SIU/ACK - Notification of cancellation of service/resource on appointment
      S21    SIU/ACK - Notification of discontinuation of service/resource on appointment
      S22    SIU/ACK - Notification of deletion of service/resource on appointment
      S23    SIU/ACK - Notification of blocked schedule time slot(s)
      S24    SIU/ACK - Notification of opened (“unblocked”) schedule time slot(s)
      S25    SQM/SQR - Schedule query message and response
      S26    SIU/ACK Notification that patient did not show up for schedule appointment
      T01    MDM/ACK - Original document notification
      T02    MDM/ACK - Original document notification and content
      T03    MDM/ACK - Document status change notification
      T04    MDM/ACK - Document status change notification and content
      T05    MDM/ACK - Document addendum notification
      T06    MDM/ACK - Document addendum notification and content
      T07    MDM/ACK - Document edit notification
      T08    MDM/ACK - Document edit notification and content
      T09    MDM/ACK - Document replacement notification
      T10    MDM/ACK - Document replacement notification and content
      T11    MDM/ACK - Document cancel notification
      T12    QRY/DOC - Document query
      U01    ESU/ACK – Automated equipment status update
      U02    ESR/ACK – Automated equipment status request
      U03    SSU/ACK - Specimen status update
      U04    SSR/ACK - specimen status request




     Value        Description                                                                Comment
      U05         INU/ACK - Automated equipment inventory update
      U06         INR/ACK – Automated equipment inventory request
      U07         EAC/ACK – Automated equipment command
      U08         EAR/ACK – Automated equipment response
      U09         EAN/ACK – Automated equipment notification
      U10         TCU/ACK – Automated equipment test code settings update
      U11         TCR/ACK – Automated equipment test code settings request
      U12         LSU/ACK – Automated equipment log/service update
      U13         LSR/ACK – Automated equipment log/service request
      V01         VXQ - Query for vaccination record
      V02         VXX - Response to vaccination query returning multiple PID matches
      V03         VXR - Vaccination record response
      V04         VXU - Unsolicited vaccination record update
     Varies       MFQ/MFR - Master files query (use event same as asking for e.g., M05 -
                  location)
      W01         ORU - Waveform result, unsolicited transmission of requested information
      W02         QRF - Waveform result, response to query

                                           User-defined Table 0004 - Patient Class
                                Value        Description                    Comment
                                 E           Emergency
                                 I           Inpatient
                                 O           Outpatient
                                 P           Preadmit
                                 R           Recurring patient
                                 B           Obstetrics
                                 C           Commercial Account
                                 N           Not Applicable
                                 U           Unknown

          “Commercial Account” is used by reference labs for specimen processing when the service is billed back to
          a third party. A registration is processed for the specimen to facilitate the subsequent billing. The identity
          of the patient may be known or unknown. In either case, for billing and statistical purposes, the patient
          class is considered a commercial account due to the third party billing responsibility.

          “Not Applicable” is used only in cases where the PV1 segment itself is not applicable but is retained in the
          message definitions for backwards compatibility (for example when a managed care system sends A28,
          A29, or A31 messages to indicate the enrolment of a patient in the system and there is no scheduled "visit"
          or "encounter" and hence the entire PV1 segment is not applicable).

                                            HL7 Table 0211 - Alternate character sets
           Value           Description                                        Comment
           ASCII           The printable 7-bit ASCII character set.           (This is the default if this field is omitted)
           8859/1          The printable characters from the ISO 8859/1
                           Character set
           8859/2          The printable characters from the ISO 8859/2
                           Character set
           8859/3          The printable characters from the ISO 8859/3
                           Character set
           8859/4          The printable characters from the ISO 8859/4
                           Character set
           8859/5          The printable characters from the ISO 8859/5
                           Character set
           8859/6          The printable characters from the ISO 8859/6
                           Character set
           8859/7          The printable characters from the ISO 8859/7
                           Character set
           8859/8          The printable characters from the ISO 8859/8
                           Character set
           8859/9          The printable characters from the ISO 8859/9
                           Character set
          ISO IR14         Code for Information Exchange (one byte)(JIS       Note that the code contains a space, i.e. "ISO IR14".
                           X 0201-1976).
          ISO IR87         Code for the Japanese Graphic Character set        Note that the code contains a space, i.e. "ISO IR87".
                           for information interchange (JIS X 0208-1990),
                                                                              The JIS X 0208 needs an escape sequence. In
                                                                              Japan, the escape technique is ISO 2022. From
                                                                              basic ASCII, escape sequence "escape" $ B (in
                                                                              HEX, 1B 24 42) lets the parser know that following
                                                                              bytes should be handled 2-byte wise. Back to ASCII
                                                                              is 1B 28 42.
         ISO IR159         Code of the supplementary Japanese Graphic         Note that the code contains a space, i.e. "ISO
                           Character set for information interchange (JIS     IR159".
                           X 0212-1990).
      GB 18030-2000        Code for Chinese Character Set (GB 18030-          Does not need an escape sequence.
                           2000)
       KS X 1001           Code for Korean Character Set (KS X 1001)
     CNS 11643-1992        Code for Taiwanese Character Set (CNS              Does not need an escape sequence.
                           11643-1992)
           BIG-5           Code for Taiwanese Character Set (BIG-5)           Does not need an escape sequence.

                                                                              BIG-5 does not need an escape sequence. ASCII is
                                                                              a 7 bit character set, which means that the top bit of
                                                                              the byte is "0". The parser knows that when the top
                                                                              bit of the byte is "0", the character set is ASCII.
                                                                              When it is "1", the following bytes should be handled
                                                                              as 2 bytes (or more). No escape technique is
                                                                              needed. However, since some servers do not
                                                                              correctly interpret when they receive a top bit "1", it
                                                                              is advised, in internet RFC, to not use these kind of
                                                                              non-safe non-escape extension.
         UNICODE           The world wide character standard from             Deprecated. Retained for backward compatibility
                           ISO/IEC 10646-1-19936                              only as v 2.5. Replaced by specific Unicode
                                                                              encoding codes.



6
    Available from The Unicode Consortium, P.O. Box 700519, San Jose, CA 95170-0519. See
    http://www/unicode.org/unicode/consortium/consort.html




       Value             Description                                   Comment
   UNICODE UTF-8         UCS Transformation Format, 8-bit form         UTF-8 is a variable-length encoding, each code
                                                                       value is represented by 1,2 or 3 bytes, depending on
                                                                       the code value. 7 bit ASCII is a proper subset of
                                                                       UTF-8. Note that the code contains a space before
                                                                       UTF but not before and after the hyphen.
   UNICODE UTF-16        UCS Transformation Format, 16-bit form        UTF-16 is identical to ISO/IEC 10646 UCS-2. Note
                                                                       that the code contains a space before UTF but not
                                                                       before and after the hyphen.
   UNICODE UTF-32        UCS Transformation Format, 32-bit form        UTF-32 is defined by Unicode Technical Report #19,
                                                                       and is an officially recognized encoding as of
                                                                       Unicode Version 3.1. UTF-32 is a proper subset of
                                                                       ISO/IEC 10646 UCS-4. Note that the code contains
                                                                       a space before UTF but not before and after the
                                                                       hyphen.
