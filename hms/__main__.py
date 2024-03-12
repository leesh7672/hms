
import hms.hcl as hcl

if __name__ == "__main__":
    hcl.update()
    hclf = open('leed-entries.tex', 'w', encoding='utf-8')
    hclf.write(hcl.build())
    hclf.close()