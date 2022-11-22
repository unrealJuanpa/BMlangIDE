using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BMlangIDE
{
    internal class Instruction
    {
        public int id;
        public string operation;
        public string condition;
        public int r1;
        public int r2;

        public Instruction(int id, string operation, string condition, int r1, int r2)
        {
            this.id = id;
            this.operation = operation;
            this.condition = condition;
            this.r1 = r1;
            this.r2 = r2;
        }
    }
}
