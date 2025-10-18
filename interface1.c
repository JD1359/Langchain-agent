#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dberror.h"
#include "expr.h"
#include "record_mgr.h"
#include "tables.h"
#include "test_helper.h"

// Context structure to encapsulate all operation state
typedef struct OperationContext
{
    RM_TableData *tbl;
    Schema *sch;
    Record *r;
    Value *v;
} OperationContext;

// Configuration for table attributes
typedef struct AttributeConfig
{
    char **attrNames;
    DataType *types;
    int *sizes;
    int count;
} AttributeConfig;

// Forward declarations
static OperationContext* initContext();
static void cleanupContext(OperationContext *ctx);
static AttributeConfig* configureAttributes();
static void releaseAttributeConfig(AttributeConfig *cfig);
static void handleTableCreation();
static void handleTableRemoval();
static void handleRecordInsertion();
static void handleRecordDeletion();
static void handleRecordModification();
static Value* captureAttributeValue(DataType dtype, int sz);
static void displayMenu();
static int getUserSelection();

int main() {
    int choices;
    
    initRecordManager(NULL);
    
    while (1) {
        displayMenu();
        choices = getUserSelection();
        
        if (choices == 6) {
            shutdownRecordManager();
            break;
        }
        
        switch (choices) {
            case 1: handleTableCreation(); break;
            case 2: handleTableRemoval(); break;
            case 3: handleRecordInsertion(); break;
            case 4: handleRecordDeletion(); break;
            case 5: handleRecordModification(); break;
            default: printf("Selection not recognized.\n");
        }
    }
    
    return 0;
}

static void displayMenu()
{
    printf("\nDatabase Operations Menu\n");
    printf("[1] Construct Table\n");
    printf("[2] Remove Table\n");
    printf("[3] Add Entry\n");
    printf("[4] Erase Entry\n");
    printf("[5] Modify Entry\n");
    printf("[6] Exit System\n");
    printf("Choices: ");
}

static int getUserSelection()
{
    int sel;
    char buffer[100];
    
    if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
        return -1;
    }
    
    if (sscanf(buffer, "%d", &sel) != 1) {
        return -1;
    }
    
    return sel;
}

static OperationContext* initContext()
{
    OperationContext *ctx;
    ctx = (OperationContext*) malloc(sizeof(OperationContext));
    ctx->tbl = (RM_TableData*) malloc(sizeof(RM_TableData));
    ctx->sch = NULL;
    ctx->r = NULL;
    ctx->v = NULL;
    return ctx;
}

static void cleanupContext(OperationContext *ctx) {
    if (ctx->v) {
        freeVal(ctx->v);
    }
    if (ctx->r) {
        freeRecord(ctx->r);
    }
    if (ctx->tbl) {
        free(ctx->tbl);
    }
    free(ctx);
}

static AttributeConfig* configureAttributes()
{
    AttributeConfig *cfig = (AttributeConfig*)malloc(sizeof(AttributeConfig));
    int indx;
    char typeChoice;
    
    printf("Attribute count: ");
    scanf("%d", &cfig->count);
    getchar();  // Clear the newline after number input
    
    cfig->attrNames = (char**)malloc(cfig->count * sizeof(char*));
    cfig->types = (DataType*)malloc(cfig->count * sizeof(DataType));
    cfig->sizes = (int*)malloc(cfig->count * sizeof(int));
    
    for (indx = 0; indx < cfig->count; indx++)
    {
        cfig->attrNames[indx] = (char*)malloc(256);
        printf("Attribute #%d identifier: ", indx + 1);
        scanf("%s", cfig->attrNames[indx]);
        
        printf("Type (I=int, F=float, S=string, B=bool): ");
        scanf(" %c", &typeChoice);
        
        switch (typeChoice) {
            case 'I':
                cfig->types[indx] = DT_INT;
                cfig->sizes[indx] = 0;
                break;
            case 'F':
                cfig->types[indx] = DT_FLOAT;
                cfig->sizes[indx] = 0;
                break;
            case 'S':
                cfig->types[indx] = DT_STRING;
                printf("String capacity: ");
                scanf("%d", &cfig->sizes[indx]);
                break;
            case 'B':
                cfig->types[indx] = DT_BOOL;
                cfig->sizes[indx] = 0;
                break;
            default:
                cfig->types[indx] = DT_INT;
                cfig->sizes[indx] = 0;
        }
    }
    
    getchar();  // Clear the final newline before returning
    
    return cfig;
}
static void releaseAttributeConfig(AttributeConfig *cfig)
{
    for (int i = 0; i < cfig->count; i++)
    {
        free(cfig->attrNames[i]);
    }
    free(cfig->attrNames);
    free(cfig->types);
    free(cfig->sizes);
    free(cfig);
}

static void handleTableCreation()
{
    char tblName[256];
    AttributeConfig *cfig;
    Schema *s;
    
    printf("Table identifier: ");
    scanf("%s", tblName);
    
    cfig = configureAttributes();  // Fixed: was 'cfg'
    s = createSchema(cfig->count, cfig->attrNames, cfig->types, cfig->sizes, 0, NULL);
    createTable(tblName, s);
    
    releaseAttributeConfig(cfig);
    printf("Construction complete.\n");
}

static void handleTableRemoval()
{
    char tblName[256];
    
    printf("Table to erase: ");
    scanf("%s", tblName);
    deleteTable(tblName);
    printf("Erasure complete.\n");
}

static Value* captureAttributeValue(DataType dtype, int sz)
{
    Value *val = NULL;
    int intVal;
    float floatVal;
    bool boolVal;
    char *strVal = (char*)malloc(256);
    
    switch (dtype)
    {
        case DT_INT:
            printf("Integer: ");
            scanf("%d", &intVal);
            MAKE_VALUE(val, DT_INT, intVal);
            break;
        case DT_FLOAT:
            printf("Decimal: ");
            scanf("%f", &floatVal);
            MAKE_VALUE(val, DT_FLOAT, floatVal);
            break;
        case DT_STRING:
            printf("Text: ");
            scanf("%s", strVal);
            MAKE_STRING_VALUE(val, strVal);
            break;
        case DT_BOOL:
            printf("Boolean: ");
            scanf("%hd", &boolVal);
            MAKE_VALUE(val, DT_BOOL, boolVal);
            break;
    }
    
    free(strVal);
    return val;
}

static void handleRecordInsertion()
{
    char tblName[256];
    OperationContext *ctx = initContext();
    int entryCount, entryIdx, attrIdx;
    
    printf("Target table: ");
    scanf("%s", tblName);
    openTable(ctx->tbl, tblName);
    
    printf("Entries to add: ");
    scanf("%d", &entryCount);
    
    for (entryIdx = 0; entryIdx < entryCount; entryIdx++)
    {
        createRecord(&ctx->r, ctx->tbl->schema);
        
        for (attrIdx = 0; attrIdx < ctx->tbl->schema->numAttr; attrIdx++)
        {
            printf("%s (%d/%d): ",
                ctx->tbl->schema->attrNames[attrIdx],
                attrIdx + 1,
                ctx->tbl->schema->numAttr);
            
            ctx->v = captureAttributeValue(
                ctx->tbl->schema->dataTypes[attrIdx],
                ctx->tbl->schema->typeLength[attrIdx]
            );
            
            setAttr(ctx->r, ctx->tbl->schema, attrIdx, ctx->v);
            freeVal(ctx->v);
            ctx->v = NULL;
        }
        
        insertRecord(ctx->tbl, ctx->r);
        freeRecord(ctx->r);
        ctx->r = NULL;
    }
    
    closeTable(ctx->tbl);
    cleanupContext(ctx);
    printf("Insertion complete.\n");
}

static void handleRecordDeletion()
{
    char tblName[256];
    OperationContext *ctx = initContext();
    int delCount, delIdx, targetAttr;
    
    printf("Target table: ");
    scanf("%s", tblName);
    openTable(ctx->tbl, tblName);
    
    printf("Deletions to perform: ");
    scanf("%d", &delCount);
    
    for (delIdx = 0; delIdx < delCount; delIdx++)
    {
        createRecord(&ctx->r, ctx->tbl->schema);
        
        printf("Select criterion attribute:\n");
        for (int i = 0; i < ctx->tbl->schema->numAttr; i++)
        {
            printf("[%d] %s\n", i, ctx->tbl->schema->attrNames[i]);
        }
        
        scanf("%d", &targetAttr);
        
        if (targetAttr >= 0 && targetAttr < ctx->tbl->schema->numAttr)
        {
            ctx->v = captureAttributeValue(
                ctx->tbl->schema->dataTypes[targetAttr],
                ctx->tbl->schema->typeLength[targetAttr]
            );
            
            setAttr(ctx->r, ctx->tbl->schema, targetAttr, ctx->v);
            deleteRecord(ctx->tbl, ctx->r->id);
            
            freeVal(ctx->v);
            ctx->v = NULL;
        }
        
        freeRecord(ctx->r);
        ctx->r = NULL;
    }
    
    closeTable(ctx->tbl);
    cleanupContext(ctx);
    printf("Deletion complete.\n");
}

static void handleRecordModification()
{
    char tblName[256];
    OperationContext *ctx = initContext();
    int modCount, modIdx, targetAttr;
    
    printf("Target table: ");
    scanf("%s", tblName);
    openTable(ctx->tbl, tblName);
    
    printf("Modifications to perform: ");
    scanf("%d", &modCount);
    
    printf("Attribute to modify:\n");
    for (int i = 0; i < ctx->tbl->schema->numAttr; i++)
    {
        printf("[%d] %s\n", i, ctx->tbl->schema->attrNames[i]);
    }
    scanf("%d", &targetAttr);
    
    if (targetAttr >= 0 && targetAttr < ctx->tbl->schema->numAttr)
    {
        for (modIdx = 0; modIdx < modCount; modIdx++)
        {
            createRecord(&ctx->r, ctx->tbl->schema);
            
            ctx->v = captureAttributeValue(
                ctx->tbl->schema->dataTypes[targetAttr],
                ctx->tbl->schema->typeLength[targetAttr]
            );
            
            setAttr(ctx->r, ctx->tbl->schema, targetAttr, ctx->v);
            updateRecord(ctx->tbl, ctx->r);
            
            freeVal(ctx->v);
            ctx->v = NULL;
            freeRecord(ctx->r);
            ctx->r = NULL;
        }
    }
    
    closeTable(ctx->tbl);
    cleanupContext(ctx);
    printf("Modification complete.\n");
}